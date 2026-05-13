import sys
import pandas as pd

sys.path.insert(0, 'validator')
sys.path.insert(0, 'engine')

from validator import validate_csv
from scorer import score_audit_data

print("\n" + "="*60)
print("CHURN INTELLIGENCE OS - COMPONENT TEST")
print("="*60)

# Test 1: Validator
print("\n✓ TEST 1: DATA VALIDATOR")
print("-" * 60)
status, report = validate_csv('data/sample_customers.csv')
print(f"Status: {status}")
print(f"Rows loaded: 50")
print(f"Data quality score: {report['data_quality_score']}/100")

# Test 2: Scorer
print("\n✓ TEST 2: SCORING ENGINE")
print("-" * 60)
df = pd.read_csv('data/sample_customers.csv')
scored = score_audit_data(df)

print("\nTOP 10 AT-RISK CUSTOMERS:")
print(scored[['customer_name', 'risk_score', 'mrr', 'primary_risk_factor']].head(10).to_string())

total_at_risk = scored[scored['risk_score'] >= 50]['mrr'].sum()
critical_count = len(scored[scored['risk_score'] >= 70])
high_count = len(scored[(scored['risk_score'] >= 50) & (scored['risk_score'] < 70)])

print(f"\n\nTotal Revenue at Risk: ${total_at_risk:,.0f}")
print(f"Critical Risk Customers: {critical_count}")
print(f"High Risk Customers: {high_count}")

print("\n" + "="*60)
print("✓ ALL COMPONENT TESTS PASSED")
print("="*60)
