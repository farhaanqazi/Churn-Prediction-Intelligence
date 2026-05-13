import sys
import pandas as pd

sys.path.insert(0, 'engine')
sys.path.insert(0, 'reports')

from scorer import score_audit_data
from report import generate_audit_pdf

# Load and score data
df = pd.read_csv('data/sample_customers.csv')
scored = score_audit_data(df)

# Generate PDF
print("Generating PDF report...")
pdf_path = generate_audit_pdf('TechFlow Inc', scored, 'reports/test_audit_report.pdf')
print(f"✓ PDF generated: {pdf_path}")
