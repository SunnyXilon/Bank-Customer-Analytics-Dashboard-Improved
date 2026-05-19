# Bank Customer Analytics Dashboard

A Dash and Plotly banking analytics dashboard with CSV-backed customer and transaction data.

## Features

- Customer, deposit, loan, revenue, churn, active, risk, and high-value KPI cards.
- Banking insights for risk score, high-value customers, loan-to-income ratio, churn risk segments, average revenue per customer, and deposit-to-loan ratio.
- Customer growth, account segmentation, revenue, age, risk, branch, product usage, and transaction trend charts.
- Full customer table with search, sorting, native filtering, CSV export, Indian currency formatting, and row highlighting.
- Transaction table with branch, city, channel, type, amount, and customer details.
- Realistic generated CSV data with names, cities, branches, occupations, product usage, and transaction records.

## Data

The app stores generated source data in:

- `data/customers.csv`
- `data/transactions.csv`

If those files are missing or outdated, the app regenerates them automatically.

## Run Locally

```bash
pip install -r requirements.txt
python app.py
```

Open:

```text
http://127.0.0.1:8052/
```

## Stack

- Python
- Dash
- Plotly
- Pandas
- NumPy
- Dash Bootstrap Components
