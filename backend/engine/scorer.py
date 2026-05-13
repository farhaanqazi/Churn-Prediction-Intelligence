"""
Churn Intelligence OS - Scoring Engine
Rule-based churn risk scoring. No machine learning — pure signal detection.
Outputs: Risk score (0-100) + primary risk factor for each customer.
"""

import pandas as pd
from typing import Tuple


class ChurnScorer:
    """
    Rule-based churn risk scorer for SaaS customers.
    
    Scoring rules:
    1. Login drop >50% month-over-month = High Risk (60 pts)
    2. Support tickets > 2 in 7d = Medium Risk (40 pts)  
    3. No payment in 45+ days = High Risk (70 pts)
    4. Zero logins in 30d = High Risk (55 pts)
    """
    
    # Risk thresholds (tuneable)
    LOGIN_DROP_THRESHOLD = 0.50  # 50% drop
    SUPPORT_TICKET_THRESHOLD = 2
    PAYMENT_THRESHOLD_DAYS = 45
    NO_LOGIN_THRESHOLD_DAYS = 30
    
    def __init__(self):
        self.scores = []
        self.risk_factors = []
    
    def score_customer(self, customer: pd.Series) -> Tuple[int, str, list]:
        """
        Score a single customer.
        
        Returns:
            (risk_score: 0-100, primary_risk_factor: str, all_signals: list)
        """
        
        score = 0
        signals = []
        
        # Signal 1: Login drop
        logins_30d = customer.get('login_count_30d', 0)
        logins_prev_30d = customer.get('login_count_prev_30d', 0)
        
        if logins_prev_30d > 0:
            login_drop_pct = (logins_prev_30d - logins_30d) / logins_prev_30d
        else:
            login_drop_pct = 0
        
        if login_drop_pct >= self.LOGIN_DROP_THRESHOLD:
            score += 60
            signals.append({
                'factor': 'login_drop',
                'severity': 'HIGH',
                'value': f"Login drop: -{login_drop_pct*100:.0f}%",
                'weight': 60
            })
        elif logins_30d == 0 and logins_prev_30d > 0:
            score += 55
            signals.append({
                'factor': 'zero_logins',
                'severity': 'HIGH',
                'value': 'No login activity in 30 days',
                'weight': 55
            })
        
        # Signal 2: Support tickets (friction signal)
        support_tickets = customer.get('support_tickets_7d', 0)
        if support_tickets > self.SUPPORT_TICKET_THRESHOLD:
            score += 40
            signals.append({
                'factor': 'support_friction',
                'severity': 'MEDIUM',
                'value': f'{support_tickets} open support tickets',
                'weight': 40
            })
        
        # Signal 3: Payment recency
        days_since_payment = customer.get('days_since_last_payment', 0)
        if days_since_payment >= self.PAYMENT_THRESHOLD_DAYS:
            score += 70
            signals.append({
                'factor': 'payment_recency',
                'severity': 'HIGH',
                'value': f'No payment in {days_since_payment} days',
                'weight': 70
            })
        
        # Cap score at 100
        score = min(score, 100)
        
        # Determine primary risk factor (highest weight signal)
        if signals:
            primary_signal = max(signals, key=lambda x: x['weight'])
            primary_risk_factor = primary_signal['value']
        else:
            primary_risk_factor = 'Low risk — all signals healthy'
        
        return score, primary_risk_factor, signals
    
    def score_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Score all customers in a DataFrame.
        
        Returns:
            DataFrame with added columns: risk_score, primary_risk_factor, signal_count
        """
        
        df = df.copy()
        df['risk_score'] = 0
        df['primary_risk_factor'] = ''
        df['signal_count'] = 0
        df['revenue_at_risk'] = 0.0
        
        for idx, row in df.iterrows():
            score, primary_factor, signals = self.score_customer(row)
            df.at[idx, 'risk_score'] = score
            df.at[idx, 'primary_risk_factor'] = primary_factor
            df.at[idx, 'signal_count'] = len(signals)
            df.at[idx, 'revenue_at_risk'] = row.get('mrr', 0) if score >= 50 else 0
        
        # Sort by risk score descending
        df = df.sort_values('risk_score', ascending=False)
        
        return df
    
    @staticmethod
    def get_risk_category(score: int) -> str:
        """Categorise risk score."""
        if score >= 70:
            return 'CRITICAL'
        elif score >= 50:
            return 'HIGH'
        elif score >= 30:
            return 'MEDIUM'
        else:
            return 'LOW'


def score_audit_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convenience function: validate + score a customer dataframe.
    
    Expected columns: customer_name, mrr, login_count_30d, login_count_prev_30d, 
                     support_tickets_7d, days_since_last_payment
    
    Returns:
        Scored DataFrame sorted by risk (highest first)
    """
    
    scorer = ChurnScorer()
    scored_df = scorer.score_dataframe(df)
    
    # Add risk category
    scored_df['risk_category'] = scored_df['risk_score'].apply(ChurnScorer.get_risk_category)
    
    return scored_df


# Example usage
if __name__ == '__main__':
    # Test data
    test_data = {
        'customer_name': ['Acme Corp', 'TechFlow Ltd', 'BuilderBase', 'StableInc'],
        'mrr': [2400, 1800, 950, 5000],
        'login_count_30d': [5, 2, 0, 450],
        'login_count_prev_30d': [150, 15, 50, 445],
        'support_tickets_7d': [0, 3, 1, 1],
        'days_since_last_payment': [90, 15, 3, 5]
    }
    
    test_df = pd.DataFrame(test_data)
    scored = score_audit_data(test_df)
    print(scored[['customer_name', 'risk_score', 'primary_risk_factor', 'revenue_at_risk']])
