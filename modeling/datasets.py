"""Dataset discovery and normalization for public churn benchmarks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


RAW_DIR = Path(__file__).parent / "data" / "raw"


@dataclass(frozen=True)
class DatasetConfig:
    name: str
    display_name: str
    filename_options: tuple[str, ...]
    target_column: str
    positive_label: str | int
    drop_columns: tuple[str, ...] = ()
    drop_column_prefixes: tuple[str, ...] = ()
    review_columns: tuple[str, ...] = ()
    strict_drop_columns: tuple[str, ...] = ()
    notes: str = ""


DATASETS: tuple[DatasetConfig, ...] = (
    DatasetConfig(
        name="iranian_churn",
        display_name="UCI Iranian Churn",
        filename_options=(
            "iranian_churn/Customer Churn.csv",
            "Customer Churn.csv",
        ),
        target_column="Churn",
        positive_label=1,
        review_columns=("Status", "Customer Value"),
        strict_drop_columns=("Status",),
        notes="Telecom churn with behavior window before churn outcome.",
    ),
    DatasetConfig(
        name="ibm_telco",
        display_name="IBM Telco Customer Churn",
        filename_options=(
            "ibm_telco/WA_Fn-UseC_-Telco-Customer-Churn.csv",
            "WA_Fn-UseC_-Telco-Customer-Churn.csv",
        ),
        target_column="Churn",
        positive_label="Yes",
        drop_columns=("customerID",),
        review_columns=("TotalCharges",),
        notes="Common benchmark dataset; useful for pipeline sanity checks.",
    ),
    DatasetConfig(
        name="credit_card_customers",
        display_name="Credit Card Customers",
        filename_options=(
            "credit_card_customers/BankChurners.csv",
            "BankChurners.csv",
        ),
        target_column="Attrition_Flag",
        positive_label="Attrited Customer",
        drop_columns=("CLIENTNUM",),
        drop_column_prefixes=("Naive_Bayes_Classifier_",),
        review_columns=("Total_Amt_Chng_Q4_Q1", "Total_Ct_Chng_Q4_Q1"),
        notes="Behavioral attrition dataset; drops leakage columns shipped with Kaggle file.",
    ),
    DatasetConfig(
        name="bank_churn",
        display_name="Bank Customer Churn",
        filename_options=(
            "bank_churn/Bank Customer Churn Prediction.csv",
            "Bank Customer Churn Prediction.csv",
        ),
        target_column="churn",
        positive_label=1,
        drop_columns=("customer_id",),
        review_columns=("active_member",),
        notes="Static bank account churn benchmark; weaker SaaS analogy.",
    ),
    DatasetConfig(
        name="ecommerce_behavior",
        display_name="E-commerce Customer Behavior Churn",
        filename_options=(
            "ecommerce_behavior/ecommerce_customer_churn_dataset.csv",
            "ecommerce_customer_churn_dataset.csv",
        ),
        target_column="Churned",
        positive_label=1,
        review_columns=("Lifetime_Value", "Credit_Balance"),
        strict_drop_columns=("Lifetime_Value",),
        notes="Recent e-commerce behavior-style churn dataset; source realism must be verified.",
    ),
    DatasetConfig(
        name="ecommerce_churn",
        display_name="E-commerce Customer Churn",
        filename_options=(
            "ecommerce_churn/data_ecommerce_customer_churn.csv",
            "data_ecommerce_customer_churn.csv",
        ),
        target_column="Churn",
        positive_label=1,
        review_columns=("Complain", "DaySinceLastOrder", "CashbackAmount"),
        notes="Compact e-commerce churn dataset with behavior and satisfaction fields.",
    ),
)


@dataclass(frozen=True)
class LoadedDataset:
    config: DatasetConfig
    path: Path
    features: pd.DataFrame
    target: pd.Series
    leakage_mode: str
    dropped_for_leakage: tuple[str, ...]


def discover_datasets(raw_dir: Path = RAW_DIR) -> list[tuple[DatasetConfig, Path]]:
    """Return configured datasets whose raw files exist locally."""
    discovered: list[tuple[DatasetConfig, Path]] = []
    for config in DATASETS:
        for option in config.filename_options:
            candidate = raw_dir / option
            if candidate.exists():
                discovered.append((config, candidate))
                break
    return discovered


def load_dataset(name: str, raw_dir: Path = RAW_DIR, strict_leakage: bool = False) -> LoadedDataset:
    """Load one configured dataset by name."""
    matches = [item for item in discover_datasets(raw_dir) if item[0].name == name]
    if not matches:
        known = ", ".join(config.name for config in DATASETS)
        raise FileNotFoundError(f"Dataset '{name}' not found in {raw_dir}. Known datasets: {known}")

    config, path = matches[0]
    df = pd.read_csv(path)
    df.columns = [str(column).strip() for column in df.columns]

    if config.target_column not in df.columns:
        raise ValueError(f"{config.display_name} missing target column '{config.target_column}'")

    target = normalize_target(df[config.target_column], config.positive_label)
    features = df.drop(columns=[config.target_column])
    features = drop_unusable_columns(features, config)
    dropped_for_leakage = tuple(column for column in config.strict_drop_columns if column in features.columns)
    if strict_leakage and dropped_for_leakage:
        features = features.drop(columns=list(dropped_for_leakage), errors="ignore")
    features = coerce_numeric_like_columns(features)

    return LoadedDataset(
        config=config,
        path=path,
        features=features,
        target=target,
        leakage_mode="strict" if strict_leakage else "standard",
        dropped_for_leakage=dropped_for_leakage if strict_leakage else (),
    )


def load_all_datasets(raw_dir: Path = RAW_DIR) -> list[LoadedDataset]:
    return [load_dataset(config.name, raw_dir) for config, _ in discover_datasets(raw_dir)]


def normalize_target(series: pd.Series, positive_label: str | int) -> pd.Series:
    if isinstance(positive_label, str):
        return series.astype(str).str.strip().eq(positive_label).astype(int)
    return pd.to_numeric(series, errors="coerce").eq(positive_label).astype(int)


def drop_unusable_columns(features: pd.DataFrame, config: DatasetConfig) -> pd.DataFrame:
    to_drop = set(column for column in config.drop_columns if column in features.columns)

    for column in features.columns:
        if any(str(column).startswith(prefix) for prefix in config.drop_column_prefixes):
            to_drop.add(column)
            continue
        unique_ratio = features[column].nunique(dropna=True) / max(len(features), 1)
        if unique_ratio > 0.98:
            to_drop.add(column)
        elif features[column].nunique(dropna=True) <= 1:
            to_drop.add(column)

    return features.drop(columns=sorted(to_drop), errors="ignore")


def coerce_numeric_like_columns(features: pd.DataFrame) -> pd.DataFrame:
    coerced = features.copy()
    for column in coerced.columns:
        if not (
            pd.api.types.is_object_dtype(coerced[column])
            or pd.api.types.is_string_dtype(coerced[column])
        ):
            continue
        numeric = pd.to_numeric(coerced[column], errors="coerce")
        non_null = coerced[column].notna().sum()
        numeric_non_null = numeric.notna().sum()
        if non_null and numeric_non_null / non_null >= 0.9:
            coerced[column] = numeric
        else:
            coerced[column] = coerced[column].astype("string")
    return coerced
