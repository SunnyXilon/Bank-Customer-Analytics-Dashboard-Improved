from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CUSTOMER_CSV = DATA_DIR / "customers.csv"
TRANSACTION_CSV = DATA_DIR / "transactions.csv"

STATES = [
    "Maharashtra", "Karnataka", "Delhi", "Gujarat",
    "Tamil Nadu", "Rajasthan", "West Bengal", "Uttar Pradesh"
]

STATE_CITIES = {
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik"],
    "Karnataka": ["Bengaluru", "Mysuru", "Mangaluru", "Hubballi"],
    "Delhi": ["New Delhi", "Dwarka", "Rohini", "Saket"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Salem"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota"],
    "West Bengal": ["Kolkata", "Howrah", "Durgapur", "Siliguri"],
    "Uttar Pradesh": ["Lucknow", "Noida", "Kanpur", "Varanasi"],
}

ACCOUNT_TYPES = ["Savings", "Current", "Premium", "Corporate"]
GENDERS = ["Male", "Female"]
OCCUPATIONS = [
    "Salaried", "Business Owner", "Self Employed", "Student",
    "Retired", "Doctor", "Engineer", "Teacher"
]
CHANNELS = ["UPI", "ATM", "Net Banking", "Branch", "Card", "NEFT"]
TRANSACTION_TYPES = ["Deposit", "Withdrawal", "Transfer", "Bill Payment", "Loan EMI"]

REQUIRED_CUSTOMER_COLUMNS = {
    "customer_id", "customer_name", "age", "gender", "state", "city",
    "branch_id", "branch_name", "occupation", "account_type", "balance",
    "loan_amount", "monthly_income", "transaction_count", "revenue",
    "credit_score", "join_date", "is_active", "churn", "has_credit_card",
    "has_fixed_deposit", "has_active_loan", "uses_savings", "uses_current",
    "risk_score", "risk_segment", "high_value_customer", "high_loan_customer",
    "loan_to_income_ratio", "deposit_to_loan_ratio", "month"
}


def _indian_names(rng, n):
    first_names = [
        "Aarav", "Vivaan", "Aditya", "Arjun", "Ishaan", "Riya", "Ananya",
        "Kavya", "Diya", "Meera", "Rohan", "Neha", "Priya", "Rahul"
    ]
    last_names = [
        "Sharma", "Verma", "Patel", "Reddy", "Iyer", "Gupta", "Singh",
        "Das", "Mehta", "Joshi", "Khan", "Nair", "Rao", "Chatterjee"
    ]
    return [
        f"{rng.choice(first_names)} {rng.choice(last_names)}"
        for _ in range(n)
    ]


def _pick_city_and_branch(rng, state):
    city = rng.choice(STATE_CITIES[state])
    branch_id = f"{state[:2].upper()}-{city[:3].upper()}-{rng.integers(1, 5):02d}"
    branch_name = f"{city} {rng.choice(['Central', 'West', 'East', 'North', 'South'])} Branch"
    return city, branch_id, branch_name


def _risk_segment(score):
    if score >= 70:
        return "High"
    if score >= 40:
        return "Medium"
    return "Low"


def enrich_customer_data(df):
    df = df.copy()
    df["join_date"] = pd.to_datetime(df["join_date"])
    df["month"] = df["join_date"].dt.to_period("M").astype(str)
    df["has_active_loan"] = df["loan_amount"] > 0

    annual_income = df["monthly_income"].replace(0, np.nan) * 12
    df["loan_to_income_ratio"] = (df["loan_amount"] / annual_income).fillna(0).round(2)
    df["deposit_to_loan_ratio"] = np.where(
        df["loan_amount"] > 0,
        (df["balance"] / df["loan_amount"]).round(2),
        0
    )

    credit_risk = (900 - df["credit_score"]) / 600 * 35
    leverage_risk = np.clip(df["loan_to_income_ratio"], 0, 1.5) / 1.5 * 25
    churn_risk = df["churn"] * 20
    activity_risk = np.where(df["is_active"] == "Inactive", 15, 0)
    balance_risk = np.where(df["balance"] < 50000, 5, 0)
    df["risk_score"] = np.clip(
        credit_risk + leverage_risk + churn_risk + activity_risk + balance_risk,
        0,
        100
    ).round(0).astype(int)
    df["risk_segment"] = df["risk_score"].apply(_risk_segment)
    df["high_value_customer"] = np.where(
        (df["balance"] >= df["balance"].quantile(0.85))
        | (df["revenue"] >= df["revenue"].quantile(0.85)),
        "Yes",
        "No"
    )
    df["high_loan_customer"] = np.where(df["loan_to_income_ratio"] >= 0.8, "Yes", "No")
    return df


def generate_customer_data(n=5000):
    rng = np.random.default_rng(42)
    join_dates = pd.date_range(start="2021-01-01", end="2026-01-01", periods=n)
    states = rng.choice(STATES, n)
    city_branch = [_pick_city_and_branch(rng, state) for state in states]

    account_type = rng.choice(ACCOUNT_TYPES, n, p=[0.42, 0.28, 0.18, 0.12])
    monthly_income = rng.integers(20000, 280000, n)
    loan_probability = np.where(account_type == "Corporate", 0.72, 0.48)
    has_loan = rng.random(n) < loan_probability
    loan_amount = np.where(has_loan, rng.integers(50000, 2500000, n), 0)
    balance = rng.integers(5000, 2500000, n)
    transaction_count = rng.integers(12, 850, n)
    credit_score = rng.integers(300, 901, n)

    df = pd.DataFrame({
        "customer_id": np.arange(1000, 1000 + n),
        "customer_name": _indian_names(rng, n),
        "age": rng.integers(18, 71, n),
        "gender": rng.choice(GENDERS, n),
        "state": states,
        "city": [item[0] for item in city_branch],
        "branch_id": [item[1] for item in city_branch],
        "branch_name": [item[2] for item in city_branch],
        "occupation": rng.choice(OCCUPATIONS, n),
        "account_type": account_type,
        "balance": balance,
        "loan_amount": loan_amount,
        "monthly_income": monthly_income,
        "transaction_count": transaction_count,
        "revenue": np.maximum(
            (balance * rng.uniform(0.008, 0.04, n))
            + (transaction_count * rng.uniform(12, 42, n))
            + (loan_amount * rng.uniform(0.002, 0.014, n)),
            1000
        ).round(0).astype(int),
        "credit_score": credit_score,
        "join_date": join_dates,
        "is_active": rng.choice(["Active", "Inactive"], n, p=[0.82, 0.18]),
        "churn": rng.choice([0, 1], n, p=[0.86, 0.14]),
        "has_credit_card": rng.choice([True, False], n, p=[0.58, 0.42]),
        "has_fixed_deposit": rng.choice([True, False], n, p=[0.36, 0.64]),
        "uses_savings": np.isin(account_type, ["Savings", "Premium"]),
        "uses_current": np.isin(account_type, ["Current", "Corporate"]),
    })

    return enrich_customer_data(df)


def generate_transaction_data(customers, n=24000):
    rng = np.random.default_rng(84)
    sampled = customers.sample(n=n, replace=True, random_state=84).reset_index(drop=True)
    dates = pd.to_datetime(
        rng.choice(pd.date_range(start="2025-01-01", end="2026-05-01", freq="D"), n)
    )
    transaction_type = rng.choice(TRANSACTION_TYPES, n, p=[0.28, 0.22, 0.24, 0.18, 0.08])
    amount = rng.lognormal(mean=9.5, sigma=0.9, size=n).round(0).astype(int)

    return pd.DataFrame({
        "transaction_id": np.arange(500000, 500000 + n),
        "customer_id": sampled["customer_id"],
        "customer_name": sampled["customer_name"],
        "transaction_date": dates,
        "transaction_type": transaction_type,
        "channel": rng.choice(CHANNELS, n),
        "amount": amount,
        "state": sampled["state"],
        "city": sampled["city"],
        "branch_id": sampled["branch_id"],
        "branch_name": sampled["branch_name"],
    })


def load_or_create_data():
    DATA_DIR.mkdir(exist_ok=True)
    regenerate = True

    if CUSTOMER_CSV.exists() and TRANSACTION_CSV.exists():
        customers = pd.read_csv(CUSTOMER_CSV)
        regenerate = not REQUIRED_CUSTOMER_COLUMNS.issubset(customers.columns)
    else:
        customers = pd.DataFrame()

    if regenerate:
        customers = generate_customer_data()
        transactions = generate_transaction_data(customers)
        customers.to_csv(CUSTOMER_CSV, index=False)
        transactions.to_csv(TRANSACTION_CSV, index=False)
    else:
        transactions = pd.read_csv(TRANSACTION_CSV)
        customers = enrich_customer_data(customers)

    transactions["transaction_date"] = pd.to_datetime(transactions["transaction_date"])
    transactions["month"] = transactions["transaction_date"].dt.to_period("M").astype(str)
    return customers, transactions


customer_df, transaction_df = load_or_create_data()


def filter_customer_data(selected_states, selected_accounts, selected_gender, age_range):
    df = customer_df.copy()
    min_age, max_age = age_range or [18, 70]

    df = df[(df["age"] >= min_age) & (df["age"] <= max_age)]

    if selected_states:
        df = df[df["state"].isin(selected_states)]

    if selected_accounts:
        df = df[df["account_type"].isin(selected_accounts)]

    if selected_gender:
        df = df[df["gender"].isin(selected_gender)]

    return df


def filter_transaction_data(customer_ids):
    if len(customer_ids) == 0:
        return transaction_df.iloc[0:0].copy()
    return transaction_df[transaction_df["customer_id"].isin(customer_ids)].copy()
