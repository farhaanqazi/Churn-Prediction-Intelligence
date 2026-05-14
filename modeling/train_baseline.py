"""Train baseline churn models and write a performance-gate report."""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    precision_recall_curve,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from datasets import DATASETS, RAW_DIR, DatasetConfig, LoadedDataset, discover_datasets, load_dataset


REPORT_DIR = Path(__file__).parent / "reports"
REPORT_PATH = REPORT_DIR / "model_report.json"
MARKDOWN_REPORT_PATH = REPORT_DIR / "model_report.md"

GATE = {
    "top_10_lift_min": 2.5,
    "pr_auc_lift_min": 1.5,
    "brier_must_beat_dummy": True,
    "monotonic_adjacent_rate_min": 0.7,
}

FEATURE_IMPORTANCE_TOP_N = 15

AUTO_REVIEW_TERMS = {
    "attrition": "feature name resembles churn/outcome language",
    "churn": "feature name resembles churn/outcome language",
    "cancel": "feature name resembles churn/outcome language",
}


def build_preprocessor(features: pd.DataFrame) -> ColumnTransformer:
    numeric_columns = features.select_dtypes(include=["number", "bool"]).columns.tolist()
    categorical_columns = [column for column in features.columns if column not in numeric_columns]

    return ColumnTransformer(
        transformers=[
            (
                "numeric",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric_columns,
            ),
            (
                "categorical",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        (
                            "onehot",
                            OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                        ),
                    ]
                ),
                categorical_columns,
            ),
        ],
        remainder="drop",
    )


def model_specs(random_state: int) -> dict[str, Any]:
    return {
        "dummy_prior": DummyClassifier(strategy="prior"),
        "logistic_regression": LogisticRegression(
            max_iter=1000,
            solver="liblinear",
            class_weight="balanced",
            random_state=random_state,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=150,
            min_samples_leaf=10,
            class_weight="balanced_subsample",
            random_state=random_state,
            n_jobs=-1,
        ),
        "gradient_boosting": GradientBoostingClassifier(random_state=random_state),
    }


def train_and_evaluate_dataset(
    dataset: LoadedDataset,
    random_state: int,
    test_size: float,
) -> dict[str, Any]:
    X_train, X_test, y_train, y_test = train_test_split(
        dataset.features,
        dataset.target,
        test_size=test_size,
        stratify=dataset.target,
        random_state=random_state,
    )

    model_results = []

    for model_name, estimator in model_specs(random_state).items():
        pipeline = Pipeline(
            steps=[
                ("preprocessor", build_preprocessor(X_train)),
                ("model", estimator),
            ]
        )
        pipeline.fit(X_train, y_train)
        probabilities = pipeline.predict_proba(X_test)[:, 1]
        result = evaluate_predictions(model_name, y_test, probabilities)
        result["top_features"] = extract_feature_importance(
            pipeline,
            original_columns=dataset.features.columns.tolist(),
            config=dataset.config,
            top_n=FEATURE_IMPORTANCE_TOP_N,
        )
        model_results.append(result)

    dummy = next(result for result in model_results if result["model"] == "dummy_prior")
    best = choose_best_model(model_results)
    gate_result = evaluate_gate(best, dummy)

    return {
        "dataset": dataset.config.name,
        "run_id": f"{dataset.config.name}_{dataset.leakage_mode}",
        "display_name": dataset.config.display_name,
        "leakage_mode": dataset.leakage_mode,
        "dropped_for_leakage": list(dataset.dropped_for_leakage),
        "source_path": str(dataset.path),
        "notes": dataset.config.notes,
        "rows": int(len(dataset.target)),
        "features": int(dataset.features.shape[1]),
        "positive_rate": round(float(dataset.target.mean()), 6),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "target_positive_label": dataset.config.positive_label,
        "models": model_results,
        "best_model": best["model"],
        "best_model_top_features": best.get("top_features", []),
        "best_model_review_flags": [
            feature
            for feature in best.get("top_features", [])
            if feature["review_status"] != "clear"
        ],
        "gate": gate_result,
    }


def evaluate_predictions(model_name: str, y_true: pd.Series, probabilities: np.ndarray) -> dict[str, Any]:
    y_array = np.asarray(y_true)
    prevalence = float(np.mean(y_array))
    positive_count = int(np.sum(y_array))

    precision, recall, _ = precision_recall_curve(y_array, probabilities)
    deciles = build_decile_table(y_array, probabilities)

    result = {
        "model": model_name,
        "roc_auc": safe_metric(lambda: roc_auc_score(y_array, probabilities)),
        "pr_auc": safe_metric(lambda: average_precision_score(y_array, probabilities)),
        "baseline_positive_rate": round(prevalence, 6),
        "brier_score": safe_metric(lambda: brier_score_loss(y_array, probabilities)),
        "top_10": top_fraction_metrics(y_array, probabilities, 0.1),
        "top_20": top_fraction_metrics(y_array, probabilities, 0.2),
        "deciles": deciles,
        "monotonic_adjacent_rate": monotonic_adjacent_rate(deciles),
        "positive_count": positive_count,
        "test_rows": int(len(y_array)),
    }

    if result["pr_auc"] is not None and prevalence > 0:
        result["pr_auc_lift"] = round(result["pr_auc"] / prevalence, 6)
    else:
        result["pr_auc_lift"] = None

    if len(recall) and positive_count:
        result["max_recall_reported"] = round(float(np.max(recall)), 6)

    return result


def top_fraction_metrics(y_true: np.ndarray, probabilities: np.ndarray, fraction: float) -> dict[str, Any]:
    n = max(1, int(math.ceil(len(y_true) * fraction)))
    order = np.argsort(probabilities)[::-1]
    selected = y_true[order[:n]]
    prevalence = float(np.mean(y_true))
    selected_rate = float(np.mean(selected))
    positives = int(np.sum(y_true))

    return {
        "fraction": fraction,
        "rows": int(n),
        "churn_rate": round(selected_rate, 6),
        "lift": round(selected_rate / prevalence, 6) if prevalence else None,
        "recall": round(float(np.sum(selected) / positives), 6) if positives else None,
    }


def build_decile_table(y_true: np.ndarray, probabilities: np.ndarray) -> list[dict[str, Any]]:
    frame = pd.DataFrame({"target": y_true, "score": probabilities})
    frame["decile"] = pd.qcut(
        frame["score"].rank(method="first", ascending=False),
        q=10,
        labels=False,
        duplicates="drop",
    )

    rows: list[dict[str, Any]] = []
    for decile, group in frame.groupby("decile", sort=True):
        rows.append(
            {
                "risk_decile": int(decile) + 1,
                "rows": int(len(group)),
                "avg_score": round(float(group["score"].mean()), 6),
                "churn_rate": round(float(group["target"].mean()), 6),
            }
        )
    return rows


def monotonic_adjacent_rate(deciles: list[dict[str, Any]]) -> float | None:
    if len(deciles) < 2:
        return None
    checks = []
    for left, right in zip(deciles, deciles[1:]):
        checks.append(left["churn_rate"] >= right["churn_rate"])
    return round(sum(checks) / len(checks), 6)


def safe_metric(metric_fn):
    try:
        return round(float(metric_fn()), 6)
    except ValueError:
        return None


def extract_feature_importance(
    pipeline: Pipeline,
    original_columns: list[str],
    config: DatasetConfig,
    top_n: int,
) -> list[dict[str, Any]]:
    model = pipeline.named_steps["model"]
    preprocessor = pipeline.named_steps["preprocessor"]

    if not hasattr(preprocessor, "get_feature_names_out"):
        return []

    feature_names = [clean_transformed_feature_name(name) for name in preprocessor.get_feature_names_out()]

    if hasattr(model, "feature_importances_"):
        values = np.asarray(model.feature_importances_)
        importance_type = "feature_importance"
    elif hasattr(model, "coef_"):
        values = np.abs(np.asarray(model.coef_)[0])
        importance_type = "absolute_coefficient"
    else:
        return []

    if len(values) != len(feature_names):
        return []

    total = float(np.sum(values))
    order = np.argsort(values)[::-1][:top_n]
    rows: list[dict[str, Any]] = []
    for rank, index in enumerate(order, start=1):
        transformed_feature = feature_names[index]
        raw_feature = infer_raw_feature(transformed_feature, original_columns)
        review_status, review_reason = classify_feature_review(raw_feature, config)
        importance = float(values[index])
        rows.append(
            {
                "rank": rank,
                "feature": transformed_feature,
                "raw_feature": raw_feature,
                "importance": round(importance, 8),
                "relative_importance": round(importance / total, 8) if total else None,
                "importance_type": importance_type,
                "review_status": review_status,
                "review_reason": review_reason,
            }
        )
    return rows


def clean_transformed_feature_name(name: str) -> str:
    if "__" in name:
        return name.split("__", 1)[1]
    return name


def infer_raw_feature(transformed_feature: str, original_columns: list[str]) -> str:
    if transformed_feature in original_columns:
        return transformed_feature

    for column in sorted(original_columns, key=len, reverse=True):
        if transformed_feature == column or transformed_feature.startswith(f"{column}_"):
            return column

    return transformed_feature


def classify_feature_review(raw_feature: str, config: DatasetConfig) -> tuple[str, str | None]:
    if raw_feature in config.strict_drop_columns:
        return "high_risk", "dropped in strict leakage mode"
    if raw_feature in config.review_columns:
        return "review", "requires source-semantics review before product use"

    lower_name = raw_feature.lower()
    if lower_name in {"status", "account_status", "customer_status", "subscription_status"}:
        return "review", "status-like field may reveal current or final customer state"

    for term, reason in AUTO_REVIEW_TERMS.items():
        if term in lower_name:
            return "review", reason

    return "clear", None


def choose_best_model(model_results: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = [result for result in model_results if result["model"] != "dummy_prior"]
    return max(
        candidates,
        key=lambda result: (
            result["top_10"]["lift"] or 0,
            result["pr_auc_lift"] or 0,
            result["roc_auc"] or 0,
        ),
    )


def evaluate_gate(best: dict[str, Any], dummy: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "top_10_lift": {
            "value": best["top_10"]["lift"],
            "minimum": GATE["top_10_lift_min"],
            "passed": (best["top_10"]["lift"] or 0) >= GATE["top_10_lift_min"],
        },
        "pr_auc_lift": {
            "value": best["pr_auc_lift"],
            "minimum": GATE["pr_auc_lift_min"],
            "passed": (best["pr_auc_lift"] or 0) >= GATE["pr_auc_lift_min"],
        },
        "brier_beats_dummy": {
            "value": best["brier_score"],
            "dummy_value": dummy["brier_score"],
            "passed": best["brier_score"] is not None
            and dummy["brier_score"] is not None
            and best["brier_score"] < dummy["brier_score"],
        },
        "monotonic_adjacent_rate": {
            "value": best["monotonic_adjacent_rate"],
            "minimum": GATE["monotonic_adjacent_rate_min"],
            "passed": (best["monotonic_adjacent_rate"] or 0) >= GATE["monotonic_adjacent_rate_min"],
        },
    }
    return {
        "passed": all(check["passed"] for check in checks.values()),
        "checks": checks,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train churn baseline models.")
    parser.add_argument(
        "--dataset",
        default="all",
        help="Dataset name to train, or 'all'.",
    )
    parser.add_argument(
        "--raw-dir",
        default=str(RAW_DIR),
        help="Directory containing raw dataset CSVs.",
    )
    parser.add_argument(
        "--report-path",
        default=str(REPORT_PATH),
        help="Output JSON report path.",
    )
    parser.add_argument(
        "--markdown-report-path",
        default=str(MARKDOWN_REPORT_PATH),
        help="Output markdown summary path.",
    )
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument(
        "--leakage-mode",
        choices=("standard", "strict", "both"),
        default="standard",
        help="standard keeps review columns, strict drops configured high-risk columns, both compares both.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_dir = Path(args.raw_dir)

    if args.dataset == "all":
        discovered = discover_datasets(raw_dir)
        if not discovered:
            expected = ", ".join(config.name for config in DATASETS)
            raise FileNotFoundError(f"No known datasets found in {raw_dir}. Expected one of: {expected}")
        dataset_names = [config.name for config, _ in discovered]
    else:
        dataset_names = [args.dataset]

    strict_modes = [False, True] if args.leakage_mode == "both" else [args.leakage_mode == "strict"]
    datasets = [
        load_dataset(dataset_name, raw_dir, strict_leakage=strict_mode)
        for dataset_name in dataset_names
        for strict_mode in strict_modes
    ]

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "raw_dir": str(raw_dir),
        "leakage_mode": args.leakage_mode,
        "gate_definition": GATE,
        "feature_importance_top_n": FEATURE_IMPORTANCE_TOP_N,
        "datasets": [
            train_and_evaluate_dataset(dataset, args.random_state, args.test_size)
            for dataset in datasets
        ],
    }

    report_path = Path(args.report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    markdown_report_path = Path(args.markdown_report_path)
    markdown_report_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_report_path.write_text(build_markdown_report(report), encoding="utf-8")

    print(f"Wrote model report: {report_path}")
    print(f"Wrote markdown summary: {markdown_report_path}")
    for dataset_result in report["datasets"]:
        gate = "PASS" if dataset_result["gate"]["passed"] else "FAIL"
        best = dataset_result["best_model"]
        lift = next(
            result for result in dataset_result["models"] if result["model"] == best
        )["top_10"]["lift"]
        flags = len(dataset_result["best_model_review_flags"])
        print(
            f"{dataset_result['dataset']} [{dataset_result['leakage_mode']}]: "
            f"{gate} | best={best} | top_10_lift={lift} | review_flags={flags}"
        )


def build_markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Churn Model Report",
        "",
        f"Generated at: `{report['generated_at']}`",
        f"Leakage mode: `{report['leakage_mode']}`",
        "",
        "## Summary",
        "",
        "| Dataset run | Gate | Best model | Top 10% lift | PR-AUC | ROC-AUC | Review flags |",
        "|---|---:|---|---:|---:|---:|---:|",
    ]

    for dataset_result in report["datasets"]:
        best = best_model_result(dataset_result)
        lines.append(
            "| {run_id} | {gate} | {model} | {lift} | {pr_auc} | {roc_auc} | {flags} |".format(
                run_id=dataset_result["run_id"],
                gate="PASS" if dataset_result["gate"]["passed"] else "FAIL",
                model=dataset_result["best_model"],
                lift=best["top_10"]["lift"],
                pr_auc=best["pr_auc"],
                roc_auc=best["roc_auc"],
                flags=len(dataset_result["best_model_review_flags"]),
            )
        )

    lines.extend(["", "## Strict Comparison", ""])
    lines.extend(strict_comparison_lines(report["datasets"]))

    lines.extend(["", "## Top Features", ""])
    for dataset_result in report["datasets"]:
        lines.extend(
            [
                f"### {dataset_result['run_id']}",
                "",
                "| Rank | Feature | Raw feature | Relative importance | Review |",
                "|---:|---|---|---:|---|",
            ]
        )
        for feature in dataset_result["best_model_top_features"][:10]:
            review = feature["review_status"]
            if feature["review_reason"]:
                review = f"{review}: {feature['review_reason']}"
            lines.append(
                "| {rank} | {feature} | {raw} | {importance} | {review} |".format(
                    rank=feature["rank"],
                    feature=feature["feature"],
                    raw=feature["raw_feature"],
                    importance=feature["relative_importance"],
                    review=review,
                )
            )
        lines.append("")

    return "\n".join(lines)


def strict_comparison_lines(dataset_results: list[dict[str, Any]]) -> list[str]:
    by_dataset: dict[str, dict[str, dict[str, Any]]] = {}
    for result in dataset_results:
        by_dataset.setdefault(result["dataset"], {})[result["leakage_mode"]] = result

    if not any("standard" in runs and "strict" in runs for runs in by_dataset.values()):
        return ["Strict comparison requires `--leakage-mode both`.", ""]

    lines = [
        "| Dataset | Standard top 10% lift | Strict top 10% lift | Delta | Strict dropped columns |",
        "|---|---:|---:|---:|---|",
    ]
    for dataset_name, runs in by_dataset.items():
        if "standard" not in runs or "strict" not in runs:
            continue
        standard_best = best_model_result(runs["standard"])
        strict_best = best_model_result(runs["strict"])
        standard_lift = standard_best["top_10"]["lift"]
        strict_lift = strict_best["top_10"]["lift"]
        delta = round(strict_lift - standard_lift, 6)
        dropped = ", ".join(runs["strict"]["dropped_for_leakage"]) or "None"
        lines.append(f"| {dataset_name} | {standard_lift} | {strict_lift} | {delta} | {dropped} |")
    lines.append("")
    return lines


def best_model_result(dataset_result: dict[str, Any]) -> dict[str, Any]:
    return next(
        result
        for result in dataset_result["models"]
        if result["model"] == dataset_result["best_model"]
    )


if __name__ == "__main__":
    main()
