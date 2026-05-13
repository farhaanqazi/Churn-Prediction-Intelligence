"""
Churn Intelligence OS - PDF Report Generator
Generates branded audit reports with risk table and interpretation.
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from datetime import datetime
import pandas as pd
from io import BytesIO


class ChurnAuditReportGenerator:
    """Generate professional PDF audit reports."""
    
    def __init__(self, filename=None):
        self.filename = filename or f"Churn_Audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Create custom paragraph styles."""
        
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#666666'),
            spaceAfter=18,
            fontName='Helvetica'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHead',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=10,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='Interpretation',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            alignment=0,  # Left align
            spaceAfter=12,
            leading=14
        ))
    
    def generate_pdf(self, company_name: str, scored_df: pd.DataFrame, output_path=None):
        """
        Generate a complete audit PDF.
        
        Args:
            company_name: Name of audited company
            scored_df: DataFrame with risk_score, primary_risk_factor, mrr columns
            output_path: Where to save PDF (defaults to self.filename)
        """
        
        if output_path is None:
            output_path = self.filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
            title=f'Churn Audit — {company_name}'
        )
        
        # Build content
        elements = []
        
        # Header
        header_text = f"<font name='Helvetica-Bold' size='20'>Churn Intelligence Audit</font>"
        elements.append(Paragraph(header_text, self.styles['CustomTitle']))
        elements.append(Paragraph(f"<b>{company_name}</b> — {datetime.now().strftime('%B %d, %Y')}", 
                                 self.styles['Subtitle']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Key Metrics Section
        elements.append(Paragraph("Key Findings", self.styles['SectionHead']))
        
        total_revenue_at_risk = scored_df[scored_df['risk_score'] >= 50]['mrr'].sum()
        high_risk_count = len(scored_df[scored_df['risk_score'] >= 70])
        critical_customers = scored_df[scored_df['risk_score'] >= 70]['customer_name'].tolist()
        
        summary_text = f"""
        <b>Total Revenue at Risk (next 60 days):</b> ${total_revenue_at_risk:,.0f}<br/>
        <b>Critical Risk Customers:</b> {high_risk_count}<br/>
        <b>Audit Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}
        """
        elements.append(Paragraph(summary_text, self.styles['Interpretation']))
        elements.append(Spacer(1, 0.15*inch))
        
        # Risk Table
        elements.append(Paragraph("Customer Risk Assessment", self.styles['SectionHead']))
        
        # Build table data
        table_data = [['Customer', 'Risk Score', 'MRR', 'Primary Signal', 'Category']]
        
        for _, row in scored_df.head(20).iterrows():
            customer = row.get('customer_name', 'N/A')[:25]  # Truncate long names
            risk_score = int(row.get('risk_score', 0))
            mrr = f"${row.get('mrr', 0):,.0f}"
            signal = str(row.get('primary_risk_factor', 'N/A'))[:40]
            category = self._risk_to_color_tag(risk_score)
            
            table_data.append([customer, str(risk_score), mrr, signal, category])
        
        # Create table with styling
        table = Table(table_data, colWidths=[1.8*inch, 1*inch, 1*inch, 1.8*inch, 1*inch])
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Body rows
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            
            # Center numeric columns
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
            ('ALIGN', (4, 1), (4, -1), 'CENTER'),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Interpretation
        elements.append(Paragraph("What This Means", self.styles['SectionHead']))
        
        interpretation = self._generate_interpretation(scored_df, total_revenue_at_risk)
        elements.append(Paragraph(interpretation, self.styles['Interpretation']))
        
        elements.append(Spacer(1, 0.15*inch))
        
        # Recommendations
        elements.append(Paragraph("Next Steps", self.styles['SectionHead']))
        
        next_steps = self._generate_recommendations(scored_df, high_risk_count)
        elements.append(Paragraph(next_steps, self.styles['Interpretation']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Footer
        footer = """
        <font size='8' color='#999999'>
        This audit was generated by Churn Intelligence OS. It identifies customers at risk based on 
        login activity, support friction, and payment history. Scores are updated weekly. For questions, 
        contact your Fractional Churn Intelligence Officer.
        </font>
        """
        elements.append(Paragraph(footer, self.styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        
        return output_path
    
    def _risk_to_color_tag(self, score: int) -> str:
        """Convert score to risk category."""
        if score >= 70:
            return '🔴 CRITICAL'
        elif score >= 50:
            return '🟠 HIGH'
        elif score >= 30:
            return '🟡 MEDIUM'
        else:
            return '🟢 LOW'
    
    def _generate_interpretation(self, df: pd.DataFrame, total_at_risk: float) -> str:
        """Generate interpretation text."""
        
        high_risk = len(df[df['risk_score'] >= 70])
        med_risk = len(df[(df['risk_score'] >= 50) & (df['risk_score'] < 70)])
        
        text = f"""
        <b>Revenue at Risk:</b> ${total_at_risk:,.0f} across {high_risk + med_risk} customers.<br/>
        <br/>
        <b>Risk Breakdown:</b><br/>
        • {high_risk} customers at CRITICAL risk (score ≥70)<br/>
        • {med_risk} customers at HIGH risk (score 50–69)<br/>
        <br/>
        The revenue at risk represents customers who may churn within the next 60 days based on 
        their current activity patterns. Immediate attention from your CS team is recommended for 
        all CRITICAL customers this week.
        """
        return text
    
    def _generate_recommendations(self, df: pd.DataFrame, critical_count: int) -> str:
        """Generate recommendations."""
        
        text = "<b>Recommended Priority Actions:</b><br/>"
        
        if critical_count > 0:
            top_signal = df[df['risk_score'] >= 70]['primary_risk_factor'].value_counts().index[0]
            text += f"""
            1. <b>This week:</b> Schedule QBRs with all {critical_count} CRITICAL customers.<br/>
            2. <b>Primary issue to address:</b> {top_signal}<br/>
            3. <b>Track progress:</b> Request weekly updates from CS team on these accounts.<br/>
            """
        else:
            text += """
            1. Continue monitoring these accounts weekly.<br/>
            2. Proactively reach out to HIGH risk customers with check-in calls.<br/>
            3. Investigate any sudden score increases — they may signal new issues.<br/>
            """
        
        return text


def generate_audit_pdf(company_name: str, scored_df: pd.DataFrame, output_path: str = None) -> str:
    """Convenience function to generate audit PDF."""
    
    generator = ChurnAuditReportGenerator()
    return generator.generate_pdf(company_name, scored_df, output_path)


# Example usage
if __name__ == '__main__':
    test_data = {
        'customer_name': ['Acme Corp', 'TechFlow Ltd', 'BuilderBase'],
        'mrr': [2400, 1800, 950],
        'risk_score': [87, 74, 71],
        'primary_risk_factor': ['Login drop: -68% (30d)', '3 open support tickets', 'No login in 18 days']
    }
    
    test_df = pd.DataFrame(test_data)
    pdf_path = generate_audit_pdf('Example Company', test_df)
    print(f"PDF generated: {pdf_path}")
