from pathlib import Path
import sys
import tempfile

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"
SAMPLE_CSV = ROOT_DIR / "data" / "sample_customers.csv"

sys.path.insert(0, str(BACKEND_DIR))

from engine.scorer import score_audit_data
from reports.report import generate_audit_pdf


df = pd.read_csv(SAMPLE_CSV)
scored = score_audit_data(df)

print("Generating PDF report...")
with tempfile.TemporaryDirectory() as temp_dir:
    output_path = Path(temp_dir) / "test_audit_report.pdf"
    pdf_path = Path(generate_audit_pdf("TechFlow Inc", scored, str(output_path)))

    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 1000

    print(f"PDF generated: {pdf_path}")
