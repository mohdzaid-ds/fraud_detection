import streamlit as st
import pandas as pd
import joblib
from datetime import datetime, timedelta

# -------------------------------
# Load model and fraud rules
# -------------------------------
model = joblib.load("best_fraud_model_1.pkl")
fraud_rules = joblib.load("fraud_rules.pkl")

terminal_fraud_days = fraud_rules["terminal_fraud_days"]
customer_fraud_days = fraud_rules["customer_fraud_days"]

# -------------------------------
# Streamlit UI
# -------------------------------
st.title("💳 Fraud Detection App")

st.write("Enter transaction details to check if it's fraud or not.")

# User input
tx_datetime = st.date_input("Transaction Date", datetime.now())
tx_time = st.time_input("Transaction Time", datetime.now().time())
tx_datetime = datetime.combine(tx_datetime, tx_time)

customer_id = st.number_input("Customer ID", min_value=1, step=1)
terminal_id = st.number_input("Terminal ID", min_value=1, step=1)
amount = st.number_input("Transaction Amount", min_value=0.0, step=10.0)

if st.button("🔍 Check Transaction"):
    is_fraud = False
    fraud_reason = None

    # -------------------------------
    # Rule 1: Amount > 220
    # -------------------------------
    if amount > 220:
        is_fraud = True
        fraud_reason = "🚨 FRAUD detected by Rule 1 (Amount > 220)"

    # -------------------------------
    # Rule 2: Terminal Fraud (28 days)
    # -------------------------------
    if not is_fraud and terminal_id in terminal_fraud_days:
        for start_day in terminal_fraud_days[terminal_id]:
            if start_day <= tx_datetime < start_day + timedelta(days=28):
                is_fraud = True
                fraud_reason = "🚨 FRAUD detected by Rule 2 (Terminal fraud window)"
                break

    # -------------------------------
    # Rule 3: Customer Fraud (14 days, ×5)
    # -------------------------------
    if not is_fraud and customer_id in customer_fraud_days:
        for start_day in customer_fraud_days[customer_id]:
            if start_day <= tx_datetime < start_day + timedelta(days=14) and amount % 5 == 0:
                is_fraud = True
                fraud_reason = "🚨 FRAUD detected by Rule 3 (Customer fraud window)"
                break

    # -------------------------------
    # ML Model Prediction (if no rule triggers)
    # -------------------------------
    if not is_fraud:
        features = pd.DataFrame([{
            "TX_AMOUNT": amount,
            "CUSTOMER_ID": customer_id,
            "TERMINAL_ID": terminal_id,
            "TX_DATETIME": int(tx_datetime.timestamp()),
            "AMOUNT_OVER_220": int(amount > 220)
        }])

        pred = model.predict(features)[0]
        prob = model.predict_proba(features)[0][1]

        if pred == 1:
            st.warning(f"⚠ Predicted FRAUD by ML Model — Probability: {prob:.2f}")
        else:
            st.success(f"✅ Legitimate Transaction — Fraud Probability: {prob:.2f}")

    else:
        st.error(fraud_reason)