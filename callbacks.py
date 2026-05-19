from dash import Input, Output, State, ctx
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd

from charts import create_dashboard_figures
from components import (
    create_column_defs,
    create_insight_card,
    create_kpi_card,
    create_kpi_modal_body,
    data_table,
    format_currency,
    format_indian_number,
    format_ratio,
    format_table_df,
    get_kpi_modal_config,
)
from data import filter_customer_data, filter_transaction_data


TABLE_COLUMNS = [
    "customer_id",
    "customer_name",
    "age",
    "gender",
    "state",
    "city",
    "branch_name",
    "occupation",
    "account_type",
    "balance",
    "loan_amount",
    "monthly_income",
    "revenue",
    "credit_score",
    "risk_score",
    "risk_segment",
    "loan_to_income_ratio",
    "deposit_to_loan_ratio",
    "high_value_customer",
    "high_loan_customer",
    "has_credit_card",
    "has_fixed_deposit",
    "is_active",
    "churn",
]

TRANSACTION_COLUMNS = [
    "transaction_id",
    "customer_id",
    "customer_name",
    "transaction_date",
    "transaction_type",
    "channel",
    "amount",
    "state",
    "city",
    "branch_name",
]


def _safe_ratio(numerator, denominator):
    return numerator / denominator if denominator else 0


def _trend_text(current, previous, suffix=""):
    if previous == 0:
        return "New baseline"
    delta = ((current - previous) / previous) * 100
    sign = "+" if delta >= 0 else ""
    return f"{sign}{delta:.1f}% {suffix}".strip()


def _customer_growth_trend(df):
    if df.empty:
        return "No trend"
    latest_month = df["join_date"].max()
    recent_start = latest_month - pd.Timedelta(days=180)
    previous_start = latest_month - pd.Timedelta(days=360)
    recent = len(df[df["join_date"] >= recent_start])
    previous = len(df[(df["join_date"] >= previous_start) & (df["join_date"] < recent_start)])
    return _trend_text(recent, previous, "last 6m")


def _build_insights(df):
    total_customers = len(df)
    total_deposits = df["balance"].sum()
    total_loans = df["loan_amount"].sum()
    total_revenue = df["revenue"].sum()
    avg_revenue = _safe_ratio(total_revenue, total_customers)
    deposit_to_loan = _safe_ratio(total_deposits, total_loans)
    avg_loan_income = df["loan_to_income_ratio"].mean() if total_customers else 0
    high_value = len(df[df["high_value_customer"] == "Yes"])
    high_risk = len(df[df["risk_segment"] == "High"])
    credit_card_users = int(df["has_credit_card"].sum()) if total_customers else 0

    return [
        dbc.Col(create_insight_card(
            "Average Revenue / Customer",
            format_currency(avg_revenue),
            "Revenue efficiency across the filtered portfolio.",
            "bi-cash-coin",
            "text-info"
        ), xs=12, md=6, xl=4),
        dbc.Col(create_insight_card(
            "Deposit-To-Loan Ratio",
            format_ratio(deposit_to_loan),
            "Higher values indicate stronger deposit coverage.",
            "bi-bank",
            "text-success"
        ), xs=12, md=6, xl=4),
        dbc.Col(create_insight_card(
            "High-Value Customers",
            format_indian_number(high_value),
            f"{_safe_ratio(high_value, total_customers) * 100:.1f}% of selected customers.",
            "bi-gem",
            "text-warning"
        ), xs=12, md=6, xl=4),
        dbc.Col(create_insight_card(
            "Average Loan-To-Income",
            format_ratio(avg_loan_income),
            "Portfolio leverage based on annual income.",
            "bi-percent",
            "text-danger"
        ), xs=12, md=6, xl=4),
        dbc.Col(create_insight_card(
            "High-Risk Customers",
            format_indian_number(high_risk),
            f"{_safe_ratio(high_risk, total_customers) * 100:.1f}% are in the high-risk segment.",
            "bi-shield-exclamation",
            "text-danger"
        ), xs=12, md=6, xl=4),
        dbc.Col(create_insight_card(
            "Credit Card Penetration",
            f"{_safe_ratio(credit_card_users, total_customers) * 100:.1f}%",
            "Share of customers with an active credit card.",
            "bi-credit-card-2-front",
            "text-info"
        ), xs=12, md=6, xl=4),
    ]


def _build_customer_table(df, search_customer):
    table_df = df[TABLE_COLUMNS].copy()
    if search_customer:
        table_df = table_df[
            table_df["customer_id"].astype(str).str.contains(str(search_customer), case=False, na=False)
        ]
    display_df = format_table_df(table_df)
    return data_table(
        display_df.to_dict("records"),
        create_column_defs(display_df),
        page_size=15
    )


def _build_transaction_table(transactions):
    transaction_df = transactions.sort_values("transaction_date", ascending=False)[TRANSACTION_COLUMNS].copy()
    transaction_df["transaction_date"] = transaction_df["transaction_date"].dt.strftime("%Y-%m-%d")
    display_df = format_table_df(transaction_df)
    return data_table(
        display_df.to_dict("records"),
        create_column_defs(display_df),
        page_size=12
    )


def register_callbacks(app):
    @app.callback(
        [
            Output("age-min-display", "children"),
            Output("age-max-display", "children"),
        ],
        Input("age-slider", "value")
    )
    def update_age_range_display(age_range):
        min_age, max_age = age_range or [18, 70]
        return str(min_age), str(max_age)

    @app.callback(
        [
            Output("customer-kpi", "children"),
            Output("deposit-kpi", "children"),
            Output("loan-kpi", "children"),
            Output("revenue-kpi", "children"),
            Output("churn-kpi", "children"),
            Output("active-kpi", "children"),
            Output("risk-kpi", "children"),
            Output("value-kpi", "children"),
            Output("insight-cards", "children"),
            Output("growth-chart", "figure"),
            Output("segment-chart", "figure"),
            Output("revenue-chart", "figure"),
            Output("age-chart", "figure"),
            Output("risk-chart", "figure"),
            Output("branch-chart", "figure"),
            Output("product-chart", "figure"),
            Output("transaction-chart", "figure"),
            Output("customer-table-container", "children"),
            Output("transaction-table-container", "children"),
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
        transactions = filter_transaction_data(df["customer_id"])

        total_customers = len(df)
        total_deposits = format_currency(df["balance"].sum())
        total_loans = format_currency(df["loan_amount"].sum())
        total_revenue = format_currency(df["revenue"].sum())
        churn_rate = round(df["churn"].mean() * 100, 2) if len(df) else 0
        active_customers = len(df[df["is_active"] == "Active"])
        avg_risk = df["risk_score"].mean() if len(df) else 0
        high_value = len(df[df["high_value_customer"] == "Yes"])

        active_rate = _safe_ratio(active_customers, total_customers) * 100
        high_value_rate = _safe_ratio(high_value, total_customers) * 100

        customer_kpi = create_kpi_card("Customers", format_indian_number(total_customers), "primary", "bi-people", _customer_growth_trend(df))
        deposit_kpi = create_kpi_card("Deposits", total_deposits, "success", "bi-piggy-bank", "CSV-backed")
        loan_kpi = create_kpi_card("Loans", total_loans, "warning", "bi-file-earmark-text", "Loan book")
        revenue_kpi = create_kpi_card("Revenue", total_revenue, "info", "bi-currency-rupee", "Fee + interest")
        churn_kpi = create_kpi_card("Churn Rate", f"{churn_rate}%", "danger", "bi-person-x", "At-risk signal")
        active_kpi = create_kpi_card("Active", format_indian_number(active_customers), "secondary", "bi-person-check", f"{active_rate:.1f}% active")
        risk_kpi = create_kpi_card("Avg Risk", f"{avg_risk:.1f}", "dark", "bi-shield-exclamation", "0 low - 100 high")
        value_kpi = create_kpi_card("High Value", format_indian_number(high_value), "success", "bi-gem", f"{high_value_rate:.1f}% portfolio")

        figures = create_dashboard_figures(df, transactions)
        customer_table = _build_customer_table(df, search_customer)
        transaction_table = _build_transaction_table(transactions)

        return (
            customer_kpi,
            deposit_kpi,
            loan_kpi,
            revenue_kpi,
            churn_kpi,
            active_kpi,
            risk_kpi,
            value_kpi,
            _build_insights(df),
            *figures,
            customer_table,
            transaction_table,
        )

    @app.callback(
        [
            Output("kpi-modal", "is_open"),
            Output("kpi-modal-title", "children"),
            Output("kpi-modal-body", "children"),
            Output("active-kpi-modal", "data")
        ],
        [
            Input("customer-kpi", "n_clicks"),
            Input("deposit-kpi", "n_clicks"),
            Input("loan-kpi", "n_clicks"),
            Input("revenue-kpi", "n_clicks"),
            Input("churn-kpi", "n_clicks"),
            Input("active-kpi", "n_clicks"),
            Input("risk-kpi", "n_clicks"),
            Input("value-kpi", "n_clicks"),
            Input("close-kpi-modal", "n_clicks"),
            Input("kpi-search-toggle", "value", allow_optional=True),
            Input("kpi-customer-search", "value", allow_optional=True)
        ],
        [
            State("state-filter", "value"),
            State("account-filter", "value"),
            State("gender-filter", "value"),
            State("age-slider", "value"),
            State("active-kpi-modal", "data")
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
        risk_clicks,
        value_clicks,
        close_clicks,
        search_enabled,
        customer_search,
        selected_states,
        selected_accounts,
        selected_gender,
        age_range,
        active_kpi_modal
    ):
        clicked_id = ctx.triggered_id
        click_counts = {
            "customer-kpi": customer_clicks,
            "deposit-kpi": deposit_clicks,
            "loan-kpi": loan_clicks,
            "revenue-kpi": revenue_clicks,
            "churn-kpi": churn_clicks,
            "active-kpi": active_clicks,
            "risk-kpi": risk_clicks,
            "value-kpi": value_clicks,
        }

        if clicked_id == "close-kpi-modal":
            return False, "", [], None

        if clicked_id in ["kpi-search-toggle", "kpi-customer-search"]:
            clicked_id = active_kpi_modal

        if not clicked_id or not click_counts.get(clicked_id):
            raise PreventUpdate

        df = filter_customer_data(selected_states, selected_accounts, selected_gender, age_range)
        config = get_kpi_modal_config(clicked_id, df)
        if not config:
            raise PreventUpdate

        body = create_kpi_modal_body(config, search_enabled, customer_search)

        return True, config["title"], body, clicked_id
