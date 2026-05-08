import numpy as np
import pandas as pd
from dash import Dash, html, dcc, Input, Output, dash_table
import plotly.express as px
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta

# ======================================================
# GENERATE SYNTHETIC BANKING DATA
# ======================================================

np.random.seed(42)

states = [
    "Maharashtra", "Karnataka", "Delhi", "Gujarat",
    "Tamil Nadu", "Rajasthan", "West Bengal", "Uttar Pradesh"
]

account_types = ["Savings", "Current", "Premium", "Corporate"]
genders = ["Male", "Female"]

n = 3000

join_dates = pd.date_range(start="2021-01-01", end="2026-01-01", periods=n)

customer_df = pd.DataFrame({
    "customer_id": np.arange(1000, 1000 + n),
    "age": np.random.randint(18, 70, n),
    "gender": np.random.choice(genders, n),
    "state": np.random.choice(states, n),
    "account_type": np.random.choice(account_types, n),
    "balance": np.random.randint(5000, 1000000, n),
    "loan_amount": np.random.randint(0, 500000, n),
    "monthly_income": np.random.randint(20000, 250000, n),
    "transaction_count": np.random.randint(10, 500, n),
    "revenue": np.random.randint(1000, 100000, n),
    "credit_score": np.random.randint(300, 900, n),
    "join_date": join_dates,
    "is_active": np.random.choice(["Active", "Inactive"], n, p=[0.8, 0.2]),
    "churn": np.random.choice([0, 1], n, p=[0.85, 0.15])
})

customer_df["month"] = customer_df["join_date"].dt.to_period("M").astype(str)

# ======================================================
# APP INITIALIZATION
# ======================================================

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
server = app.server

# ======================================================
# KPI CALCULATIONS
# ======================================================

def create_kpi_card(title, value, color):
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className="text-light"),
            html.H4(value, className="fw-bold")
        ]),
        color=color,
        inverse=True,
        style={"borderRadius": "15px"},
        className="h-100"
    )

# ======================================================
# LAYOUT
# ======================================================

app.layout = dbc.Container([

    # ==================================================
    # HEADER
    # ==================================================

    dbc.Row([
        dbc.Col([
            html.H1(
                "Bank Customer Analytics Dashboard",
                className="text-center text-info mb-5 mt-4"
            )
        ])
    ]),

    # ==================================================
    # FILTERS
    # ==================================================

    dbc.Row([

        dbc.Col([
            html.Label("Select State", className="mb-2"),
            dcc.Dropdown(
                id="state-filter",
                options=[{"label": i, "value": i} for i in states],
                multi=True,
                placeholder="Select states"
            )
        ], md=3),

        dbc.Col([
            html.Label("Account Type", className="mb-2"),
            dcc.Dropdown(
                id="account-filter",
                options=[{"label": i, "value": i} for i in account_types],
                multi=True,
                placeholder="Select account types"
            )
        ], md=3),

        dbc.Col([
            html.Label("Gender", className="mb-2"),
            dcc.Dropdown(
                id="gender-filter",
                options=[{"label": i, "value": i} for i in genders],
                multi=True,
                placeholder="Select gender"
            )
        ], md=2),

        dbc.Col([
            html.Label("Age Range", className="mb-2"),
            dcc.RangeSlider(
                id="age-slider",
                min=18,
                max=70,
                value=[18, 70],
                marks={18: '18', 30: '30', 50: '50', 70: '70'}
            )
        ], md=4)

    ], className="mb-5"),

    # ==================================================
    # KPI CARDS
    # ==================================================

    dbc.Row([

        dbc.Col(html.Div(id="customer-kpi", className="h-100"), md=2),
        dbc.Col(html.Div(id="deposit-kpi", className="h-100"), md=2),
        dbc.Col(html.Div(id="loan-kpi", className="h-100"), md=2),
        dbc.Col(html.Div(id="revenue-kpi", className="h-100"), md=2),
        dbc.Col(html.Div(id="churn-kpi", className="h-100"), md=2),
        dbc.Col(html.Div(id="active-kpi", className="h-100"), md=2),

    ], className="mb-5 align-items-stretch"),

    # ==================================================
    # CHARTS ROW 1
    # ==================================================

    dbc.Row([

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Customer Growth Trend", className="fs-5 p-3"),
                dbc.CardBody([
                    dcc.Graph(id="growth-chart")
                ], className="p-4")
            ], className="h-100 shadow-sm", style={"borderRadius": "15px"})
        ], md=6),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Customer Segmentation", className="fs-5 p-3"),
                dbc.CardBody([
                    dcc.Graph(id="segment-chart")
                ], className="p-4")
            ], className="h-100 shadow-sm", style={"borderRadius": "15px"})
        ], md=6)

    ], className="mb-5 align-items-stretch"),

    # ==================================================
    # CHARTS ROW 2
    # ==================================================

    dbc.Row([

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Revenue by Account Type", className="fs-5 p-3"),
                dbc.CardBody([
                    dcc.Graph(id="revenue-chart")
                ], className="p-4")
            ], className="h-100 shadow-sm", style={"borderRadius": "15px"})
        ], md=6),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Customer Age Distribution", className="fs-5 p-3"),
                dbc.CardBody([
                    dcc.Graph(id="age-chart")
                ], className="p-4")
            ], className="h-100 shadow-sm", style={"borderRadius": "15px"})
        ], md=6)

    ], className="mb-5 align-items-stretch"),


    # ==================================================
    # DATA TABLE
    # ==================================================

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    dbc.Row([
                        dbc.Col(html.Span("Customer Data Explorer"), md=8, align="center"),
                        dbc.Col(
                            dbc.Input(
                                id="search-customer",
                                type="text",
                                placeholder="Search Customer ID...",
                                className="form-control-sm"
                            ),
                            md=4
                        )
                    ])
                ], className="fs-5 p-3"),
                dbc.CardBody([
                    dash_table.DataTable(
                        id="customer-table",
                        page_size=10,
                        style_table={"overflowX": "auto"},
                        style_cell={
                            "textAlign": "left",
                            "padding": "15px",
                            "backgroundColor": "#111111",
                            "color": "white"
                        },
                        style_header={
                            "backgroundColor": "#222222",
                            "fontWeight": "bold",
                            "padding": "15px"
                        }
                    )
                ], className="p-4")
            ], className="shadow-sm", style={"borderRadius": "15px"})
        ])
    ])

], fluid=True, className="p-4")

# ======================================================
# CALLBACKS
# ======================================================

@app.callback(
    [
        Output("customer-kpi", "children"),
        Output("deposit-kpi", "children"),
        Output("loan-kpi", "children"),
        Output("revenue-kpi", "children"),
        Output("churn-kpi", "children"),
        Output("active-kpi", "children"),
        Output("growth-chart", "figure"),
        Output("segment-chart", "figure"),
        Output("revenue-chart", "figure"),
        Output("age-chart", "figure"),
        Output("customer-table", "data"),
        Output("customer-table", "columns")
    ],
    [
        Input("state-filter", "value"),
        Input("account-filter", "value"),
        Input("gender-filter", "value"),
        Input("age-slider", "value"),
        Input("search-customer", "value")
    ]
)
def update_dashboard(selected_states, selected_accounts, selected_gender, age_range, search_customer):

    df = customer_df.copy()

    # FILTERS

    df = df[(df["age"] >= age_range[0]) & (df["age"] <= age_range[1])]

    if selected_states:
        df = df[df["state"].isin(selected_states)]

    if selected_accounts:
        df = df[df["account_type"].isin(selected_accounts)]

    if selected_gender:
        df = df[df["gender"].isin(selected_gender)]

    # ==================================================
    # KPI VALUES
    # ==================================================

    total_customers = len(df)
    total_deposits = f"₹{df['balance'].sum():,.0f}"
    total_loans = f"₹{df['loan_amount'].sum():,.0f}"
    total_revenue = f"₹{df['revenue'].sum():,.0f}"
    churn_rate = round(df['churn'].mean() * 100, 2)
    active_customers = len(df[df['is_active'] == 'Active'])

    customer_kpi = create_kpi_card("Customers", total_customers, "primary")
    deposit_kpi = create_kpi_card("Deposits", total_deposits, "success")
    loan_kpi = create_kpi_card("Loans", total_loans, "warning")
    revenue_kpi = create_kpi_card("Revenue", total_revenue, "info")
    churn_kpi = create_kpi_card("Churn Rate", f"{churn_rate}%", "danger")
    active_kpi = create_kpi_card("Active", active_customers, "secondary")

    # ==================================================
    # CHARTS
    # ==================================================

    # Customer Growth

    growth_df = df.groupby("month").size().reset_index(name="customers")

    growth_fig = px.line(
        growth_df,
        x="month",
        y="customers",
        markers=True,
        template="plotly_dark"
    )

    # Segmentation

    segment_fig = px.pie(
        df,
        names="account_type",
        hole=0.5,
        template="plotly_dark"
    )

    # Revenue Chart

    revenue_df = df.groupby("account_type", as_index=False)["revenue"].sum()

    revenue_fig = px.bar(
        revenue_df,
        x="account_type",
        y="revenue",
        color="account_type",
        template="plotly_dark"
    )

    # Age Distribution

    age_fig = px.histogram(
        df,
        x="age",
        nbins=25,
        template="plotly_dark"
    )


    # ==================================================
    # TABLE
    # ==================================================

    table_df = df[[
        "customer_id",
        "age",
        "gender",
        "state",
        "account_type",
        "balance",
        "loan_amount",
        "revenue",
        "credit_score"
    ]]

    if search_customer:
        table_df = table_df[table_df["customer_id"].astype(str).str.contains(str(search_customer))]

    table_df = table_df.head(50)

    data = table_df.to_dict("records")
    columns = [{"name": i, "id": i} for i in table_df.columns]

    return (
        customer_kpi,
        deposit_kpi,
        loan_kpi,
        revenue_kpi,
        churn_kpi,
        active_kpi,
        growth_fig,
        segment_fig,
        revenue_fig,
        age_fig,
        data,
        columns
    )

# ======================================================
# RUN APP
# ======================================================

if __name__ == "__main__":
    app.run(debug=True)
