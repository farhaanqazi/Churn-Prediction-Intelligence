"""
Generate sample customer data for testing the Churn Intelligence OS audit tool.
"""

import pandas as pd
import random
from datetime import datetime

def generate_sample_data(num_customers=50, save_to='sample_customers.csv'):
    """
    Generate realistic sample customer data.
    """
    
    random.seed(42)
    
    customers = []
    
    for i in range(num_customers):
        # Realistic customer names
        company_types = ['Tech', 'App', 'Digital', 'Smart', 'Cloud', 'Data', 'Cyber']
        industries = ['Corp', 'Ltd', 'Inc', 'Systems', 'Solutions', 'Labs']
        
        customer_name = f"{random.choice(company_types)}{random.choice(company_types)} {random.choice(industries)}"
        
        # Realistic MRR (monthly recurring revenue) - $500 to $50k
        mrr = random.randint(5, 500) * 100
        
        # Simulate different customer health scenarios
        scenario = random.random()
        
        if scenario < 0.1:  # 10% critical at-risk
            login_count_30d = random.randint(0, 5)
            login_count_prev_30d = random.randint(50, 200)
            support_tickets_7d = random.randint(4, 8)
            days_since_last_payment = random.randint(60, 120)
        
        elif scenario < 0.25:  # 15% high risk
            login_count_30d = random.randint(10, 30)
            login_count_prev_30d = random.randint(80, 150)
            support_tickets_7d = random.randint(2, 4)
            days_since_last_payment = random.randint(30, 60)
        
        elif scenario < 0.5:  # 25% medium risk
            login_count_30d = random.randint(30, 80)
            login_count_prev_30d = random.randint(40, 100)
            support_tickets_7d = random.randint(0, 2)
            days_since_last_payment = random.randint(1, 30)
        
        else:  # 50% healthy
            login_count_30d = random.randint(80, 300)
            login_count_prev_30d = random.randint(70, 310)
            support_tickets_7d = 0
            days_since_last_payment = random.randint(1, 15)
        
        customers.append({
            'customer_name': customer_name,
            'mrr': mrr,
            'login_count_30d': login_count_30d,
            'login_count_prev_30d': login_count_prev_30d,
            'support_tickets_7d': support_tickets_7d,
            'days_since_last_payment': days_since_last_payment
        })
    
    df = pd.DataFrame(customers)
    
    if save_to:
        df.to_csv(save_to, index=False)
        print(f"✓ Generated {len(df)} sample customers → {save_to}")
    
    return df


if __name__ == '__main__':
    # Generate and save sample data
    df = generate_sample_data(num_customers=50, save_to='sample_customers.csv')
    
    print("\nSample data preview:")
    print(df.head(10))
    print(f"\nTotal customers: {len(df)}")
    print(f"Total MRR: ${df['mrr'].sum():,.0f}")
