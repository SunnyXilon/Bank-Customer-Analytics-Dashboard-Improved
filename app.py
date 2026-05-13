import numpy as np
import pandas as pd
from dash import Dash, html, dcc, Input, Output, State, dash_table, ctx
from dash.exceptions import PreventUpdate
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

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG],
    suppress_callback_exceptions=True
)
server = app.server

# ======================================================
# KPI CALCULATIONS
# ======================================================

def filter_customer_data(selected_states, selected_accounts, selected_gender, age_range):
    df = customer_df.copy()

    df = df[(df["age"] >= age_range[0]) & (df["age"] <= age_range[1])]

    if selected_states:
        df = df[df["state"].isin(selected_states)]

    if selected_accounts:
        df = df[df["account_type"].isin(selected_accounts)]

    if selected_gender:
        df = df[df["gender"].isin(selected_gender)]

    return df


def create_kpi_card(title, value, color):
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className="kpi-title text-light"),
            html.H4(value, className="kpi-value fw-bold")
        ], className="kpi-card-body text-center p-3"),
        color=color,
        inverse=True,
        className="kpi-card h-100 shadow-sm"
    )


def create_modal_table(df):
    return dash_table.DataTable(
        data=df.to_dict("records"),
        columns=[{"name": i, "id": i} for i in df.columns],
        page_size=10,
        style_table={"overflowX": "auto", "maxHeight": "60vh", "overflowY": "auto"},
        style_cell={
            "textAlign": "left",
            "padding": "12px",
            "backgroundColor": "#111111",
            "color": "white",
            "minWidth": "110px"
        },
        style_header={
            "backgroundColor": "#222222",
            "fontWeight": "bold",
            "padding": "12px"
        }
    )


def style_chart(fig):
    fig.update_layout(
        height=360,
        margin={"l": 35, "r": 20, "t": 20, "b": 45},
        paper_bgcolor="#060606",
        plot_bgcolor="#060606",
        font={"color": "#f8f9fa"},
        legend_title_text=""
    )
    return fig

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
                className="dashboard-title text-center text-info mb-4 mt-2"
            )
        ])
    ]),

    # ==================================================
    # FILTERS
    # ==================================================

    dbc.Row([

        dbc.Col([
            html.Label("Select State", className="filter-label mb-2"),
            dcc.Dropdown(
                id="state-filter",
                options=[{"label": i, "value": i} for i in states],
                multi=True,
                placeholder="Select states"
            )
        ], xs=12, md=6, xl=3),

        dbc.Col([
            html.Label("Account Type", className="filter-label mb-2"),
            dcc.Dropdown(
                id="account-filter",
                options=[{"label": i, "value": i} for i in account_types],
                multi=True,
                placeholder="Select account types"
            )
        ], xs=12, md=6, xl=3),

        dbc.Col([
            html.Label("Gender", className="filter-label mb-2"),
            dcc.Dropdown(
                id="gender-filter",
                options=[{"label": i, "value": i} for i in genders],
                multi=True,
                placeholder="Select gender"
            )
        ], xs=12, md=4, xl=2),

        dbc.Col([
            html.Label("Age Range", className="filter-label mb-2"),
            dcc.RangeSlider(
                id="age-slider",
                min=18,
                max=70,
                value=[18, 70],
                marks={18: '18', 30: '30', 50: '50', 70: '70'}
            )
        ], xs=12, md=8, xl=4)

    ], className="g-3 align-items-end mb-4"),

    # ==================================================
    # KPI CARDS
    # ==================================================

    dbc.Row([

        dbc.Col(html.Div(id="customer-kpi", n_clicks=0, role="button", title="Open Customers data", className="kpi-click-target h-100"), xs=12, sm=6, lg=4, xl=2),
        dbc.Col(html.Div(id="deposit-kpi", n_clicks=0, role="button", title="Open Deposits data", className="kpi-click-target h-100"), xs=12, sm=6, lg=4, xl=2),
        dbc.Col(html.Div(id="loan-kpi", n_clicks=0, role="button", title="Open Loans data", className="kpi-click-target h-100"), xs=12, sm=6, lg=4, xl=2),
        dbc.Col(html.Div(id="revenue-kpi", n_clicks=0, role="button", title="Open Revenue data", className="kpi-click-target h-100"), xs=12, sm=6, lg=4, xl=2),
        dbc.Col(html.Div(id="churn-kpi", n_clicks=0, role="button", title="Open Churn Rate data", className="kpi-click-target h-100"), xs=12, sm=6, lg=4, xl=2),
        dbc.Col(html.Div(id="active-kpi", n_clicks=0, role="button", title="Open Active data", className="kpi-click-target h-100"), xs=12, sm=6, lg=4, xl=2),

    ], className="g-3 mb-4 align-items-stretch"),

    # ==================================================
    # CHARTS ROW 1
    # ==================================================

    dbc.Row([

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Customer Growth Trend", className="panel-header fs-5 px-3 py-2"),
                dbc.CardBody([
                    dcc.Graph(id="growth-chart", style={"height": "360px"})
                ], className="chart-body p-3")
            ], className="panel-card h-100 shadow-sm")
        ], xs=12, lg=6),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Customer Segmentation", className="panel-header fs-5 px-3 py-2"),
                dbc.CardBody([
                    dcc.Graph(id="segment-chart", style={"height": "360px"})
                ], className="chart-body p-3")
            ], className="panel-card h-100 shadow-sm")
        ], xs=12, lg=6)

    ], className="g-4 mb-4 align-items-stretch"),

    # ==================================================
    # CHARTS ROW 2
    # ==================================================

    dbc.Row([

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Revenue by Account Type", className="panel-header fs-5 px-3 py-2"),
                dbc.CardBody([
                    dcc.Graph(id="revenue-chart", style={"height": "360px"})
                ], className="chart-body p-3")
            ], className="panel-card h-100 shadow-sm")
        ], xs=12, lg=6),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Customer Age Distribution", className="panel-header fs-5 px-3 py-2"),
                dbc.CardBody([
                    dcc.Graph(id="age-chart", style={"height": "360px"})
                ], className="chart-body p-3")
            ], className="panel-card h-100 shadow-sm")
        ], xs=12, lg=6)

    ], className="g-4 mb-4 align-items-stretch"),


    # ==================================================
    # DATA TABLE
    # ==================================================

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    dbc.Row([
                        dbc.Col(html.Span("Customer Data Explorer"), xs=12, md=6, align="center"),
                        dbc.Col(
                            dbc.Input(
                                id="search-customer",
                                type="text",
                                placeholder="Search Customer ID...",
                                className="form-control-sm"
                            ),
                            xs=12,
                            md=6
                        )
                    ], className="g-3 align-items-center")
                ], className="fs-5 p-3"),
                dbc.CardBody([
                    dash_table.DataTable(
                        id="customer-table",
                        page_size=10,
                        style_table={"overflowX": "auto"},
                        style_cell={
                            "textAlign": "left",
                            "padding": "12px",
                            "backgroundColor": "#111111",
                            "color": "white",
                            "minWidth": "110px"
                        },
                        style_header={
                            "backgroundColor": "#222222",
                            "fontWeight": "bold",
                            "padding": "12px"
                        }
                    )
                ], className="table-card-body")
            ], className="panel-card shadow-sm")
        ])
    ], className="g-4"),

    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle(id="kpi-modal-title")),
            dbc.ModalBody(id="kpi-modal-body"),
            dbc.ModalFooter(
                dbc.Button("Close", id="close-kpi-modal", className="ms-auto", n_clicks=0)
            )
        ],
        id="kpi-modal",
        size="xl",
        is_open=False,
        scrollable=True
    )

], fluid=True, className="dashboard-shell p-4")

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

    df = filter_customer_data(selected_states, selected_accounts, selected_gender, age_range)

    # ==================================================
    # KPI VALUES
    # ==================================================

    total_customers = len(df)
    total_deposits = f"₹{df['balance'].sum():,.0f}"
    total_loans = f"₹{df['loan_amount'].sum():,.0f}"
    total_revenue = f"₹{df['revenue'].sum():,.0f}"
    churn_rate = round(df['churn'].mean() * 100, 2) if len(df) else 0
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

    growth_fig = style_chart(px.line(
        growth_df,
        x="month",
        y="customers",
        markers=True,
        template="plotly_dark"
    ))

    # Segmentation

    segment_fig = style_chart(px.pie(
        df,
        names="account_type",
        hole=0.5,
        template="plotly_dark"
    ))

    # Revenue Chart

    revenue_df = df.groupby("account_type", as_index=False)["revenue"].sum()

    revenue_fig = style_chart(px.bar(
        revenue_df,
        x="account_type",
        y="revenue",
        color="account_type",
        template="plotly_dark"
    ))

    # Age Distribution

    age_fig = style_chart(px.histogram(
        df,
        x="age",
        nbins=25,
        template="plotly_dark"
    ))


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


@app.callback(
    [
        Output("kpi-modal", "is_open"),
        Output("kpi-modal-title", "children"),
        Output("kpi-modal-body", "children")
    ],
    [
        Input("customer-kpi", "n_clicks"),
        Input("deposit-kpi", "n_clicks"),
        Input("loan-kpi", "n_clicks"),
        Input("revenue-kpi", "n_clicks"),
        Input("churn-kpi", "n_clicks"),
        Input("active-kpi", "n_clicks"),
        Input("close-kpi-modal", "n_clicks")
    ],
    [
        State("state-filter", "value"),
        State("account-filter", "value"),
        State("gender-filter", "value"),
        State("age-slider", "value")
    ],
    prevent_initial_call=True
)
def open_kpi_details(
    customer_clicks,
    deposit_clicks,
    loan_clicks,
    revenue_clicks,
    churn_clicks,
    active_clicks,
    close_clicks,
    selected_states,
    selected_accounts,
    selected_gender,
    age_range
):
    clicked_id = ctx.triggered_id
    click_counts = {
        "customer-kpi": customer_clicks,
        "deposit-kpi": deposit_clicks,
        "loan-kpi": loan_clicks,
        "revenue-kpi": revenue_clicks,
        "churn-kpi": churn_clicks,
        "active-kpi": active_clicks
    }

    if clicked_id == "close-kpi-modal":
        return False, "", []

    if not clicked_id or not click_counts.get(clicked_id):
        raise PreventUpdate

    df = filter_customer_data(selected_states, selected_accounts, selected_gender, age_range)

    modal_config = {
        "customer-kpi": {
            "title": "Customer Details",
            "summary": f"{len(df):,} customers match the current filters.",
            "df": df.sort_values("customer_id"),
            "columns": [
                "customer_id", "age", "gender", "state", "account_type",
                "balance", "loan_amount", "revenue", "credit_score", "is_active"
            ]
        },
        "deposit-kpi": {
            "title": "Deposit Details",
            "summary": f"Total deposits: Rs. {df['balance'].sum():,.0f}",
            "df": df.sort_values("balance", ascending=False),
            "columns": [
                "customer_id", "state", "account_type", "balance",
                "monthly_income", "transaction_count", "is_active"
            ]
        },
        "loan-kpi": {
            "title": "Loan Details",
            "summary": f"Total loans: Rs. {df['loan_amount'].sum():,.0f}",
            "df": df[df["loan_amount"] > 0].sort_values("loan_amount", ascending=False),
            "columns": [
                "customer_id", "state", "account_type", "loan_amount",
                "monthly_income", "credit_score", "churn"
            ]
        },
        "revenue-kpi": {
            "title": "Revenue Details",
            "summary": f"Total revenue: Rs. {df['revenue'].sum():,.0f}",
            "df": df.sort_values("revenue", ascending=False),
            "columns": [
                "customer_id", "state", "account_type", "revenue",
                "balance", "transaction_count", "is_active"
            ]
        },
        "churn-kpi": {
            "title": "Churned Customer Details",
            "summary": f"{int(df['churn'].sum()):,} customers are marked as churned.",
            "df": df[df["churn"] == 1].sort_values("revenue", ascending=False),
            "columns": [
                "customer_id", "age", "gender", "state", "account_type",
                "balance", "loan_amount", "revenue", "credit_score"
            ]
        },
        "active-kpi": {
            "title": "Active Customer Details",
            "summary": f"{len(df[df['is_active'] == 'Active']):,} customers have active account status.",
            "df": df[df["is_active"] == "Active"].sort_values("customer_id"),
            "columns": [
                "customer_id", "age", "gender", "state", "account_type",
                "balance", "loan_amount", "revenue", "credit_score"
            ]
        }
    }

    config = modal_config.get(clicked_id)
    if not config:
        raise PreventUpdate

    modal_df = config["df"][config["columns"]].head(200)

    body = [
        html.P(config["summary"], className="fs-5 mb-2"),
        html.P(
            f"Showing {len(modal_df):,} records based on the current filters.",
            className="text-muted mb-4"
        ),
        create_modal_table(modal_df)
    ]

    return True, config["title"], body

# ======================================================
# RUN APP
# ======================================================

if __name__ == "__main__":
    app.run(port=8052,debug=True)
