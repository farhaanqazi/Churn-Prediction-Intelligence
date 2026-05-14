# Churn Modeling Benchmark

This folder proves whether the ML engine has real churn signal before it is wired into the product UI.

## Raw Data

Place public datasets under `modeling/data/raw/`. The loader accepts either nested folders or the flat files currently used locally:

- `Customer Churn.csv` - UCI Iranian churn
- `WA_Fn-UseC_-Telco-Customer-Churn.csv` - IBM Telco churn
- `BankChurners.csv` - Credit Card Customers
- `Bank Customer Churn Prediction.csv` - Bank customer churn
- `ecommerce_customer_churn_dataset.csv` - e-commerce behavior churn
- `data_ecommerce_customer_churn.csv` - compact e-commerce churn

Raw data is ignored by git. Keep it local unless the dataset license explicitly allows redistribution.

## Run

```powershell
.venv\Scripts\python modeling\train_baseline.py --dataset all
```

The script writes:

```text
modeling/reports/model_report.json
modeling/reports/model_report.md
```

To compare normal training against a conservative leakage review run:

```powershell
.venv\Scripts\python modeling\train_baseline.py --dataset all --leakage-mode both
```

## Models

The benchmark trains:

- dummy prior baseline
- logistic regression
- random forest
- gradient boosting

Preprocessing is dataset-agnostic: numeric imputation/scaling plus categorical one-hot encoding. Known leakage/id columns are dropped.

The report also includes top feature importance for the best model on each dataset. Features are flagged when their column names or dataset config require leakage/source-semantics review.

## Performance Gate

A dataset/model only passes if the best non-dummy model clears all checks:

- Top 10% lift >= 2.5
- PR-AUC lift over prevalence >= 1.5
- Brier score beats dummy prior baseline
- Adjacent risk-decile monotonicity >= 0.7

Passing this gate does not prove commercial SaaS performance. It only proves the modeling system can find churn signal on real public churn data.

## Leakage Review

Leakage review is intentionally conservative:

- `standard` mode keeps all non-target features except known ID/helper leakage columns.
- `strict` mode additionally drops configured high-risk columns, currently Iranian churn `Status` and e-commerce behavior `Lifetime_Value`.
- `both` mode writes a side-by-side comparison of standard versus strict results.

Review flags do not automatically mean a feature is invalid. They mean the feature must be confirmed as available before the churn prediction date before it can be used in a product model.

## User Upload Path

The public-dataset leakage review is for training benchmark trust. User-uploaded CSVs need a separate automated path before ML scoring:

```text
upload -> validator -> leakage scanner -> schema mapper -> compatibility gate -> ML scoring or rule fallback
```

Required checks:

- reject or warn on likely target leakage columns such as `churn`, `cancelled`, `status`, `is_active`, `renewed`, `termination_date`, and `lost_reason`
- map accepted columns into the SaaS Gold feature schema
- verify required model features, types, missingness, row count, categorical handling, and distribution drift
- fall back to rule-based scoring when the upload is not compatible with the trained ML model
- report that prediction quality cannot be proven at upload time unless future churn outcomes are later supplied
