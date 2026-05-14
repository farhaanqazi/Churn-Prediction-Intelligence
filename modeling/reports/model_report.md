# Churn Model Report

Generated at: `2026-05-14T08:00:13.554975+00:00`
Leakage mode: `both`

## Summary

| Dataset run | Gate | Best model | Top 10% lift | PR-AUC | ROC-AUC | Review flags |
|---|---:|---|---:|---:|---:|---:|
| iranian_churn_standard | PASS | gradient_boosting | 5.959596 | 0.905125 | 0.974557 | 2 |
| iranian_churn_strict | PASS | gradient_boosting | 5.757576 | 0.891701 | 0.971761 | 1 |
| ibm_telco_standard | PASS | gradient_boosting | 2.912372 | 0.664096 | 0.843362 | 1 |
| ibm_telco_strict | PASS | gradient_boosting | 2.912372 | 0.664096 | 0.843362 | 1 |
| credit_card_customers_standard | PASS | gradient_boosting | 6.172429 | 0.955554 | 0.987685 | 2 |
| credit_card_customers_strict | PASS | gradient_boosting | 6.172429 | 0.955554 | 0.987685 | 2 |
| bank_churn_standard | PASS | gradient_boosting | 4.152334 | 0.723487 | 0.872286 | 1 |
| bank_churn_strict | PASS | gradient_boosting | 4.152334 | 0.723487 | 0.872286 | 1 |
| ecommerce_behavior_standard | PASS | gradient_boosting | 3.411765 | 0.903601 | 0.928007 | 1 |
| ecommerce_behavior_strict | PASS | gradient_boosting | 3.352941 | 0.857437 | 0.909983 | 0 |
| ecommerce_churn_standard | PASS | gradient_boosting | 4.8827 | 0.78133 | 0.926849 | 3 |
| ecommerce_churn_strict | PASS | gradient_boosting | 4.8827 | 0.78133 | 0.926849 | 3 |

## Strict Comparison

| Dataset | Standard top 10% lift | Strict top 10% lift | Delta | Strict dropped columns |
|---|---:|---:|---:|---|
| iranian_churn | 5.959596 | 5.757576 | -0.20202 | Status |
| ibm_telco | 2.912372 | 2.912372 | 0.0 | None |
| credit_card_customers | 6.172429 | 6.172429 | 0.0 | None |
| bank_churn | 4.152334 | 4.152334 | 0.0 | None |
| ecommerce_behavior | 3.411765 | 3.352941 | -0.058824 | Lifetime_Value |
| ecommerce_churn | 4.8827 | 4.8827 | 0.0 | None |


## Top Features

### iranian_churn_standard

| Rank | Feature | Raw feature | Relative importance | Review |
|---:|---|---|---:|---|
| 1 | Complains | Complains | 0.36245957 | clear |
| 2 | Status | Status | 0.17745753 | high_risk: dropped in strict leakage mode |
| 3 | Seconds of Use | Seconds of Use | 0.1343019 | clear |
| 4 | Frequency of use | Frequency of use | 0.09550599 | clear |
| 5 | Subscription  Length | Subscription  Length | 0.08495525 | clear |
| 6 | Distinct Called Numbers | Distinct Called Numbers | 0.05165803 | clear |
| 7 | Call  Failure | Call  Failure | 0.03690594 | clear |
| 8 | Customer Value | Customer Value | 0.02864268 | review: requires source-semantics review before product use |
| 9 | Frequency of SMS | Frequency of SMS | 0.01204618 | clear |
| 10 | Age | Age | 0.01057599 | clear |

### iranian_churn_strict

| Rank | Feature | Raw feature | Relative importance | Review |
|---:|---|---|---:|---|
| 1 | Complains | Complains | 0.40069484 | clear |
| 2 | Frequency of use | Frequency of use | 0.17928077 | clear |
| 3 | Seconds of Use | Seconds of Use | 0.14722377 | clear |
| 4 | Subscription  Length | Subscription  Length | 0.10723378 | clear |
| 5 | Customer Value | Customer Value | 0.0545307 | review: requires source-semantics review before product use |
| 6 | Call  Failure | Call  Failure | 0.03258073 | clear |
| 7 | Distinct Called Numbers | Distinct Called Numbers | 0.02256446 | clear |
| 8 | Age | Age | 0.01800502 | clear |
| 9 | Charge  Amount | Charge  Amount | 0.01574357 | clear |
| 10 | Age Group | Age Group | 0.01315173 | clear |

### ibm_telco_standard

| Rank | Feature | Raw feature | Relative importance | Review |
|---:|---|---|---:|---|
| 1 | Contract_Month-to-month | Contract | 0.37991031 | clear |
| 2 | tenure | tenure | 0.13868176 | clear |
| 3 | InternetService_Fiber optic | InternetService | 0.08654205 | clear |
| 4 | TotalCharges | TotalCharges | 0.08636484 | review: requires source-semantics review before product use |
| 5 | MonthlyCharges | MonthlyCharges | 0.08159224 | clear |
| 6 | OnlineSecurity_No | OnlineSecurity | 0.06814173 | clear |
| 7 | PaymentMethod_Electronic check | PaymentMethod | 0.04421437 | clear |
| 8 | TechSupport_No | TechSupport | 0.03785534 | clear |
| 9 | PaperlessBilling_Yes | PaperlessBilling | 0.01122717 | clear |
| 10 | MultipleLines_No | MultipleLines | 0.01030204 | clear |

### ibm_telco_strict

| Rank | Feature | Raw feature | Relative importance | Review |
|---:|---|---|---:|---|
| 1 | Contract_Month-to-month | Contract | 0.37991031 | clear |
| 2 | tenure | tenure | 0.13868176 | clear |
| 3 | InternetService_Fiber optic | InternetService | 0.08654205 | clear |
| 4 | TotalCharges | TotalCharges | 0.08636484 | review: requires source-semantics review before product use |
| 5 | MonthlyCharges | MonthlyCharges | 0.08159224 | clear |
| 6 | OnlineSecurity_No | OnlineSecurity | 0.06814173 | clear |
| 7 | PaymentMethod_Electronic check | PaymentMethod | 0.04421437 | clear |
| 8 | TechSupport_No | TechSupport | 0.03785534 | clear |
| 9 | PaperlessBilling_Yes | PaperlessBilling | 0.01122717 | clear |
| 10 | MultipleLines_No | MultipleLines | 0.01030204 | clear |

### credit_card_customers_standard

| Rank | Feature | Raw feature | Relative importance | Review |
|---:|---|---|---:|---|
| 1 | Total_Trans_Ct | Total_Trans_Ct | 0.33142419 | clear |
| 2 | Total_Trans_Amt | Total_Trans_Amt | 0.19352822 | clear |
| 3 | Total_Revolving_Bal | Total_Revolving_Bal | 0.1915352 | clear |
| 4 | Total_Ct_Chng_Q4_Q1 | Total_Ct_Chng_Q4_Q1 | 0.09853551 | review: requires source-semantics review before product use |
| 5 | Total_Relationship_Count | Total_Relationship_Count | 0.09818351 | clear |
| 6 | Total_Amt_Chng_Q4_Q1 | Total_Amt_Chng_Q4_Q1 | 0.02924265 | review: requires source-semantics review before product use |
| 7 | Months_Inactive_12_mon | Months_Inactive_12_mon | 0.01654445 | clear |
| 8 | Contacts_Count_12_mon | Contacts_Count_12_mon | 0.0161252 | clear |
| 9 | Customer_Age | Customer_Age | 0.01255487 | clear |
| 10 | Avg_Open_To_Buy | Avg_Open_To_Buy | 0.00340638 | clear |

### credit_card_customers_strict

| Rank | Feature | Raw feature | Relative importance | Review |
|---:|---|---|---:|---|
| 1 | Total_Trans_Ct | Total_Trans_Ct | 0.33142419 | clear |
| 2 | Total_Trans_Amt | Total_Trans_Amt | 0.19352822 | clear |
| 3 | Total_Revolving_Bal | Total_Revolving_Bal | 0.1915352 | clear |
| 4 | Total_Ct_Chng_Q4_Q1 | Total_Ct_Chng_Q4_Q1 | 0.09853551 | review: requires source-semantics review before product use |
| 5 | Total_Relationship_Count | Total_Relationship_Count | 0.09818351 | clear |
| 6 | Total_Amt_Chng_Q4_Q1 | Total_Amt_Chng_Q4_Q1 | 0.02924265 | review: requires source-semantics review before product use |
| 7 | Months_Inactive_12_mon | Months_Inactive_12_mon | 0.01654445 | clear |
| 8 | Contacts_Count_12_mon | Contacts_Count_12_mon | 0.0161252 | clear |
| 9 | Customer_Age | Customer_Age | 0.01255487 | clear |
| 10 | Avg_Open_To_Buy | Avg_Open_To_Buy | 0.00340638 | clear |

### bank_churn_standard

| Rank | Feature | Raw feature | Relative importance | Review |
|---:|---|---|---:|---|
| 1 | age | age | 0.39538591 | clear |
| 2 | products_number | products_number | 0.3009452 | clear |
| 3 | active_member | active_member | 0.11486445 | review: requires source-semantics review before product use |
| 4 | balance | balance | 0.09145076 | clear |
| 5 | country_Germany | country | 0.05728658 | clear |
| 6 | credit_score | credit_score | 0.02038126 | clear |
| 7 | gender_Male | gender | 0.00779791 | clear |
| 8 | gender_Female | gender | 0.00557029 | clear |
| 9 | tenure | tenure | 0.0040385 | clear |
| 10 | country_France | country | 0.00140562 | clear |

### bank_churn_strict

| Rank | Feature | Raw feature | Relative importance | Review |
|---:|---|---|---:|---|
| 1 | age | age | 0.39538591 | clear |
| 2 | products_number | products_number | 0.3009452 | clear |
| 3 | active_member | active_member | 0.11486445 | review: requires source-semantics review before product use |
| 4 | balance | balance | 0.09145076 | clear |
| 5 | country_Germany | country | 0.05728658 | clear |
| 6 | credit_score | credit_score | 0.02038126 | clear |
| 7 | gender_Male | gender | 0.00779791 | clear |
| 8 | gender_Female | gender | 0.00557029 | clear |
| 9 | tenure | tenure | 0.0040385 | clear |
| 10 | country_France | country | 0.00140562 | clear |

### ecommerce_behavior_standard

| Rank | Feature | Raw feature | Relative importance | Review |
|---:|---|---|---:|---|
| 1 | Lifetime_Value | Lifetime_Value | 0.30559818 | high_risk: dropped in strict leakage mode |
| 2 | Cart_Abandonment_Rate | Cart_Abandonment_Rate | 0.16749501 | clear |
| 3 | Discount_Usage_Rate | Discount_Usage_Rate | 0.12296455 | clear |
| 4 | Customer_Service_Calls | Customer_Service_Calls | 0.11337676 | clear |
| 5 | Days_Since_Last_Purchase | Days_Since_Last_Purchase | 0.06299916 | clear |
| 6 | Age | Age | 0.05332222 | clear |
| 7 | Total_Purchases | Total_Purchases | 0.05204011 | clear |
| 8 | Email_Open_Rate | Email_Open_Rate | 0.04577483 | clear |
| 9 | Session_Duration_Avg | Session_Duration_Avg | 0.0162644 | clear |
| 10 | Pages_Per_Session | Pages_Per_Session | 0.01283903 | clear |

### ecommerce_behavior_strict

| Rank | Feature | Raw feature | Relative importance | Review |
|---:|---|---|---:|---|
| 1 | Cart_Abandonment_Rate | Cart_Abandonment_Rate | 0.21462666 | clear |
| 2 | Discount_Usage_Rate | Discount_Usage_Rate | 0.1444647 | clear |
| 3 | Customer_Service_Calls | Customer_Service_Calls | 0.1427116 | clear |
| 4 | Total_Purchases | Total_Purchases | 0.12494818 | clear |
| 5 | Average_Order_Value | Average_Order_Value | 0.11323975 | clear |
| 6 | Days_Since_Last_Purchase | Days_Since_Last_Purchase | 0.07021151 | clear |
| 7 | Age | Age | 0.06382043 | clear |
| 8 | Email_Open_Rate | Email_Open_Rate | 0.05318657 | clear |
| 9 | Session_Duration_Avg | Session_Duration_Avg | 0.01743811 | clear |
| 10 | Returns_Rate | Returns_Rate | 0.01356038 | clear |

### ecommerce_churn_standard

| Rank | Feature | Raw feature | Relative importance | Review |
|---:|---|---|---:|---|
| 1 | Tenure | Tenure | 0.47178942 | clear |
| 2 | Complain | Complain | 0.12027176 | review: requires source-semantics review before product use |
| 3 | CashbackAmount | CashbackAmount | 0.11905062 | review: requires source-semantics review before product use |
| 4 | NumberOfAddress | NumberOfAddress | 0.09121021 | clear |
| 5 | DaySinceLastOrder | DaySinceLastOrder | 0.04630154 | review: requires source-semantics review before product use |
| 6 | SatisfactionScore | SatisfactionScore | 0.0356099 | clear |
| 7 | MaritalStatus_Single | MaritalStatus | 0.02993308 | clear |
| 8 | NumberOfDeviceRegistered | NumberOfDeviceRegistered | 0.0255094 | clear |
| 9 | WarehouseToHome | WarehouseToHome | 0.02345477 | clear |
| 10 | PreferedOrderCat_Laptop & Accessory | PreferedOrderCat | 0.01372078 | clear |

### ecommerce_churn_strict

| Rank | Feature | Raw feature | Relative importance | Review |
|---:|---|---|---:|---|
| 1 | Tenure | Tenure | 0.47178942 | clear |
| 2 | Complain | Complain | 0.12027176 | review: requires source-semantics review before product use |
| 3 | CashbackAmount | CashbackAmount | 0.11905062 | review: requires source-semantics review before product use |
| 4 | NumberOfAddress | NumberOfAddress | 0.09121021 | clear |
| 5 | DaySinceLastOrder | DaySinceLastOrder | 0.04630154 | review: requires source-semantics review before product use |
| 6 | SatisfactionScore | SatisfactionScore | 0.0356099 | clear |
| 7 | MaritalStatus_Single | MaritalStatus | 0.02993308 | clear |
| 8 | NumberOfDeviceRegistered | NumberOfDeviceRegistered | 0.0255094 | clear |
| 9 | WarehouseToHome | WarehouseToHome | 0.02345477 | clear |
| 10 | PreferedOrderCat_Laptop & Accessory | PreferedOrderCat | 0.01372078 | clear |
