"""
Churn Intelligence OS - Streamlit Web App
Free audit tool for SaaS churn prediction.
"""

import streamlit as st
import pandas as pd
import sys
import os
from io import BytesIO
from datetime import datetime

# Add backend path for imports
frontend_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(frontend_dir, '..', 'backend'))
sys.path.insert(0, backend_dir)

from validator.validator import validate_csv, format_report
from engine.scorer import score_audit_data, ChurnScorer
from reports.report import generate_audit_pdf

# ============= PAGE CONFIG =============
st.set_page_config(
    page_title="Churn Intelligence Audit",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        max-width: 1200px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #2c3e50;
    }
    .critical-risk {
        background-color: #fee2e2;
        border-left-color: #dc2626;
    }
    .high-risk {
        background-color: #fef3c7;
        border-left-color: #f59e0b;
    }
    .header-text {
        font-size: 32px;
        font-weight: bold;
        color: #1a1a1a;
    }
</style>
""", unsafe_allow_html=True)

# ============= HEADER =============
st.markdown('<p class="header-text">Churn Intelligence Audit Tool</p>', unsafe_allow_html=True)
st.markdown("**See your revenue at risk in 60 seconds.** Upload your customer CSV and get an instant audit.")

st.markdown("---")

# ============= MAIN APP =============

# Sidebar for instructions
with st.sidebar:
    st.markdown("### 📋 CSV Format Required")
    st.markdown("""
    Your CSV must include these columns:
    - `customer_name` (text)
    - `mrr` (monthly revenue)
    - `login_count_30d` (logins last 30 days)
    - `login_count_prev_30d` (logins previous 30 days)
    - `support_tickets_7d` (open tickets last 7 days)
    - `days_since_last_payment` (days)
    
    [Download Sample CSV](https://example.com/sample.csv)
    """)

# File upload
uploaded_file = st.file_uploader("Upload your customer CSV", type=['csv'])

if uploaded_file is not None:
    
    # Step 1: Validate
    st.markdown("### 1️⃣ Validating Data...")
    
    with st.spinner("Checking data quality..."):
        status, validation_report = validate_csv(uploaded_file)
    
    # Show validation result
    if status == 'PASS':
        st.success("Data validation passed!")
    elif status == 'WARN':
        st.warning("Data has warnings — audit will proceed but quality is not ideal")
    else:
        st.error("Data validation failed — cannot proceed")
        st.markdown(format_report(status, validation_report))
        st.stop()
    
    # Load and score data
    st.markdown("### Step 2: Running Churn Analysis...")
    
    with st.spinner("Scoring customers..."):
        uploaded_file.seek(0)  # Reset file pointer
        df = pd.read_csv(uploaded_file)
        scored_df = score_audit_data(df)
    
    # ============= RESULTS =============
    
    st.markdown("### Audit Results")
    
    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    total_revenue_at_risk = scored_df[scored_df['risk_score'] >= 50]['mrr'].sum()
    critical_count = len(scored_df[scored_df['risk_score'] >= 70])
    high_count = len(scored_df[(scored_df['risk_score'] >= 50) & (scored_df['risk_score'] < 70)])
    total_customers = len(scored_df)
    
    with col1:
        st.metric("Revenue at Risk", f"${total_revenue_at_risk:,.0f}")
    
    with col2:
        st.metric("Critical Risk", critical_count)
    
    with col3:
        st.metric("High Risk", high_count)
    
    with col4:
        st.metric("Total Customers", total_customers)
    
    st.markdown("---")
    
    # Main risk table
    st.markdown("#### Customer Risk Breakdown")
    
    # Format for display
    display_df = scored_df[[
        'customer_name', 'risk_score', 'mrr', 'primary_risk_factor', 'signal_count'
    ]].copy()
    
    display_df.columns = ['Customer', 'Risk Score', 'MRR', 'Primary Signal', 'Signals']
    display_df['Risk Score'] = display_df['Risk Score'].astype(str)
    display_df['MRR'] = display_df['MRR'].apply(lambda x: f"${x:,.0f}")
    display_df['Primary Signal'] = display_df['Primary Signal'].str[:50]
    
    st.dataframe(display_df, width='stretch', height=400)
    
    st.markdown("---")
    
    # ============= UPGRADE PROMPT =============
    
    st.markdown("### 🚀 Upgrade to Churn Intelligence OS")
    
    st.markdown("""
    **This free audit shows you the problem. The full OS deploys the solution.**
    
    The Churn Intelligence OS is a deployed system that:
    - Calculates daily health scores for every active customer
    - Sends your CS team a weekly action list (Red/Amber/Green)
    - Tracks which interventions actually prevent churn
    - Saves your team 5+ hours per week of manual analysis
    
    **$3,500 deployment • $1,200/month refresh • 10-day setup**
    """)
    
    col_email, col_buttons = st.columns([2, 1])
    
    with col_email:
        email = st.text_input("Your email", placeholder="you@company.com")
    
    with col_buttons:
        col_yes, col_no = st.columns(2)
        
        if col_yes.button("Show me the full OS", width='stretch'):
            if email:
                # Save email (would connect to Mailchimp in production)
                st.success(f"Check your email ({email}) — details coming in 5 mins")
                st.markdown("""
                While you wait:
                - Review your audit above and identify your top 3 at-risk accounts
                - Think about what happens if you lose 10% of MRR this month
                - Note any patterns in the 'Primary Signal' column
                """)
            else:
                st.warning("Please enter your email first")
        
        if col_no.button("Not now", width='stretch'):
            st.markdown("No problem. **This audit data is yours** — feel free to download it below.")
    
    st.markdown("---")
    
    # ============= EXPORT OPTIONS =============
    
    st.markdown("### 📥 Export Your Results")
    
    col_csv, col_pdf = st.columns(2)
    
    with col_csv:
        # CSV download
        csv_buffer = BytesIO()
        scored_df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        st.download_button(
            label="📄 Download as CSV",
            data=csv_buffer,
            file_name=f"churn_audit_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with col_pdf:
        # PDF download
        company_name = st.text_input("Company name (for PDF)", value="My Company")
        
        if st.button("📊 Generate PDF Report"):
            with st.spinner("Generating PDF..."):
                pdf_buffer = BytesIO()
                generate_audit_pdf(company_name, scored_df, "temp_report.pdf")
                
                with open("temp_report.pdf", "rb") as pdf_file:
                    pdf_bytes = pdf_file.read()
                
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"churn_audit_{company_name}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
    
    st.markdown("---")
    
    # ============= FOOTER =============
    st.markdown("""
    <div style="text-align: center; color: #999; font-size: 12px; margin-top: 40px;">
    Churn Intelligence OS · Fractional Churn Intelligence Officer · Built for founders who move fast
    </div>
    """, unsafe_allow_html=True)

else:
    # No file uploaded yet
    st.markdown("""
    ### Get Started
    
    1. **Prepare your CSV** with customer data (logins, support tickets, payment history)
    2. **Upload above** — we'll validate and audit instantly
    3. **Review results** — see which customers are at risk and why
    4. **Export or upgrade** — keep the free audit, or deploy the full OS
    
    ### What You'll Get
    - ✓ Customer risk scores (0–100)
    - ✓ Revenue at risk (next 60 days)
    - ✓ Primary churn signals for each customer
    - ✓ Actionable next steps for your CS team
    - ✓ Professional PDF report
    
    **No credit card required. No data is stored.**
    """)
    
    # Sample CSV helper
    with st.expander("📋 Need a sample CSV?"):
        st.markdown("""
        Create a CSV file with these columns:
        """)
        
        sample_data = {
            'customer_name': ['Acme Corp', 'TechFlow Ltd', 'BuilderBase'],
            'mrr': [2400, 1800, 950],
            'login_count_30d': [5, 2, 0],
            'login_count_prev_30d': [150, 15, 50],
            'support_tickets_7d': [0, 3, 1],
            'days_since_last_payment': [90, 15, 3]
        }
        
        sample_df = pd.DataFrame(sample_data)
        st.dataframe(sample_df, width='stretch')
        
        csv_buffer = BytesIO()
        sample_df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        st.download_button(
            label="📥 Download Sample CSV",
            data=csv_buffer,
            file_name="sample_customers.csv",
            mime="text/csv"
        )
