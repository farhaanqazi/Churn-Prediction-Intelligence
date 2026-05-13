"""
Churn Intelligence OS - Data Validator
Checks uploaded CSV for quality, structure, and completeness.
Output: Pass / Warn / Fail report with plain-English fixes.
"""

import pandas as pd
import io
from typing import Tuple, Dict, List

# Expected columns and their required data types
EXPECTED_COLUMNS = {
    'customer_name': 'object',
    'mrr': 'numeric',
    'login_count_30d': 'numeric',
    'login_count_prev_30d': 'numeric',
    'support_tickets_7d': 'numeric',
    'days_since_last_payment': 'numeric'
}

REQUIRED_COLUMNS = ['customer_name', 'mrr', 'login_count_30d', 'support_tickets_7d', 'days_since_last_payment']
NULL_THRESHOLD = 0.05  # 5% null threshold


def validate_csv(csv_file_or_path) -> Tuple[str, Dict]:
    """
    Validate an uploaded CSV file.
    
    Returns:
        Tuple of (status, report_dict)
        status: 'PASS', 'WARN', or 'FAIL'
        report_dict: Contains validation results and recommendations
    """
    
    report = {
        'status': 'PASS',
        'errors': [],
        'warnings': [],
        'info': [],
        'recommendations': [],
        'data_quality_score': 100
    }
    
    try:
        # Load CSV
        if isinstance(csv_file_or_path, str):
            df = pd.read_csv(csv_file_or_path)
        else:
            # Handle Streamlit file uploader
            df = pd.read_csv(io.BytesIO(csv_file_or_path.read()))
        
        # Check 1: Is data empty?
        if df.empty:
            report['status'] = 'FAIL'
            report['errors'].append('CSV is empty. No rows found.')
            return report['status'], report
        
        report['info'].append(f'✓ Loaded {len(df)} rows.')
        
        # Check 2: Required columns present?
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            report['status'] = 'FAIL'
            report['errors'].append(f"Missing required columns: {', '.join(missing_cols)}")
            report['recommendations'].append(
                f"Your CSV must include these columns: {', '.join(REQUIRED_COLUMNS)}"
            )
            return report['status'], report
        
        report['info'].append(f'✓ All required columns present.')
        
        # Check 3: Data types
        type_issues = []
        for col in df.columns:
            if col == 'customer_name':
                if not pd.api.types.is_string_dtype(df[col]):
                    type_issues.append(f"'{col}' should be text (currently {df[col].dtype})")
            elif col in ['mrr', 'login_count_30d', 'login_count_prev_30d', 'support_tickets_7d', 'days_since_last_payment']:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    type_issues.append(f"'{col}' should be numeric (currently {df[col].dtype})")
        
        if type_issues:
            report['status'] = 'WARN'
            report['warnings'].extend(type_issues)
            report['data_quality_score'] -= 15
        
        # Check 4: Null values
        null_report = []
        for col in REQUIRED_COLUMNS:
            null_pct = df[col].isnull().sum() / len(df)
            if null_pct > NULL_THRESHOLD:
                null_report.append(f"'{col}': {null_pct*100:.1f}% missing")
                report['status'] = 'FAIL'
                report['data_quality_score'] -= 20
            elif null_pct > 0:
                report['warnings'].append(f"'{col}': {null_pct*100:.1f}% missing (acceptable)")
                report['data_quality_score'] -= 5
        
        if null_report:
            report['errors'].extend(null_report)
            report['recommendations'].append(
                "Remove rows with missing values in critical columns, or fill them with 0."
            )
        
        # Check 5: Data sanity checks
        sanity_issues = []
        
        if (df['mrr'] < 0).any():
            sanity_issues.append("MRR contains negative values (should be >= 0)")
            report['data_quality_score'] -= 10
        
        if (df['login_count_30d'] < 0).any() or (df['login_count_prev_30d'] < 0).any():
            sanity_issues.append("Login counts contain negative values (should be >= 0)")
            report['data_quality_score'] -= 10
        
        if (df['days_since_last_payment'] < 0).any():
            sanity_issues.append("Days since last payment contains negative values (should be >= 0)")
            report['data_quality_score'] -= 10
        
        if sanity_issues:
            report['warnings'].extend(sanity_issues)
            report['status'] = 'WARN'
        
        # Check 6: Duplicates
        dup_count = df.duplicated(subset=['customer_name']).sum()
        if dup_count > 0:
            report['warnings'].append(f"Found {dup_count} duplicate customer names")
            report['recommendations'].append("Consider deduplicating by customer name.")
            report['data_quality_score'] -= 5
        
        # Check 7: MRR sanity
        if df['mrr'].sum() == 0:
            report['warnings'].append("Total MRR is $0 — check data source")
            report['data_quality_score'] -= 10
        
        report['info'].append(f'✓ Data quality score: {report["data_quality_score"]}/100')
        
        # Final status logic
        if report['data_quality_score'] < 60:
            report['status'] = 'FAIL'
            report['recommendations'].append("This data is too poor quality to analyse. Please fix the issues above.")
        elif report['status'] == 'FAIL':
            pass  # Already set
        elif report['data_quality_score'] < 80:
            report['status'] = 'WARN'
        
        return report['status'], report
    
    except Exception as e:
        report['status'] = 'FAIL'
        report['errors'].append(f"Error reading file: {str(e)}")
        return report['status'], report


def format_report(status: str, report_dict: Dict) -> str:
    """Format validation report for display."""
    
    lines = []
    lines.append("=" * 60)
    lines.append(f"CHURN AUDIT VALIDATION — {status}")
    lines.append("=" * 60)
    
    if report_dict['info']:
        lines.append("\n✓ INFO:")
        for item in report_dict['info']:
            lines.append(f"  {item}")
    
    if report_dict['errors']:
        lines.append("\n✗ ERRORS:")
        for item in report_dict['errors']:
            lines.append(f"  • {item}")
    
    if report_dict['warnings']:
        lines.append("\n⚠ WARNINGS:")
        for item in report_dict['warnings']:
            lines.append(f"  • {item}")
    
    if report_dict['recommendations']:
        lines.append("\n→ RECOMMENDATIONS:")
        for item in report_dict['recommendations']:
            lines.append(f"  • {item}")
    
    lines.append("\n" + "=" * 60)
    
    return "\n".join(lines)
