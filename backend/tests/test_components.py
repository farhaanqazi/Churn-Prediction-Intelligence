from pathlib import Path
import sys

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"
SAMPLE_CSV = ROOT_DIR / "data" / "sample_customers.csv"

sys.path.insert(0, str(BACKEND_DIR))

from validator.validator import validate_csv
from engine.scorer import score_audit_data


print("\n" + "=" * 60)
print("CHURN INTELLIGENCE OS - COMPONENT TEST")
print("=" * 60)

print("\nTEST 1: DATA VALIDATOR")
print("-" * 60)
status, report = validate_csv(str(SAMPLE_CSV))
print(f"Status: {status}")
print(f"Data quality score: {report['data_quality_score']}/100")

assert status in {"PASS", "WARN"}
assert report["data_quality_score"] >= 80

print("\nTEST 2: SCORING ENGINE")
print("-" * 60)
df = pd.read_csv(SAMPLE_CSV)
scored = score_audit_data(df)

assert len(scored) == len(df)
assert scored["risk_score"].between(0, 100).all()
assert {
    "risk_score",
    "primary_risk_factor",
    "revenue_at_risk",
    "risk_category",
}.issubset(scored.columns)

print("\nTOP 10 AT-RISK CUSTOMERS:")
print(
    scored[
        ["customer_name", "risk_score", "mrr", "primary_risk_factor"]
    ].head(10).to_string()
)

total_at_risk = scored[scored["risk_score"] >= 50]["mrr"].sum()
critical_count = len(scored[scored["risk_score"] >= 70])
high_count = len(scored[(scored["risk_score"] >= 50) & (scored["risk_score"] < 70)])

print(f"\n\nTotal Revenue at Risk: ${total_at_risk:,.0f}")
print(f"Critical Risk Customers: {critical_count}")
print(f"High Risk Customers: {high_count}")

print("\n" + "=" * 60)
print("ALL COMPONENT TESTS PASSED")
print("=" * 60)
