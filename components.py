from dash import html, dash_table
import dash_bootstrap_components as dbc


MONEY_COLUMNS = {"balance", "loan_amount", "monthly_income", "revenue", "amount"}
PERCENT_COLUMNS = {"loan_to_income_ratio", "deposit_to_loan_ratio"}


def format_indian_number(value):
    try:
        value = int(round(float(value)))
    except (TypeError, ValueError):
        return value

    sign = "-" if value < 0 else ""
    value = abs(value)
    text = str(value)
    if len(text) <= 3:
        return f"{sign}{text}"

    last_three = text[-3:]
    remaining = text[:-3]
    groups = []
    while len(remaining) > 2:
        groups.insert(0, remaining[-2:])
        remaining = remaining[:-2]
    if remaining:
        groups.insert(0, remaining)
    return f"{sign}{','.join(groups)},{last_three}"


def format_currency(value):
    return f"\u20b9{format_indian_number(value)}"


def format_ratio(value):
    try:
        return f"{float(value):.2f}x"
    except (TypeError, ValueError):
        return value


def format_table_df(df):
    display_df = df.copy()
    for column in display_df.columns:
        if column in MONEY_COLUMNS:
            display_df[column] = display_df[column].apply(format_currency)
        elif column in PERCENT_COLUMNS:
            display_df[column] = display_df[column].apply(format_ratio)
        elif column in {"has_credit_card", "has_fixed_deposit", "has_active_loan", "uses_savings", "uses_current"}:
            display_df[column] = display_df[column].map({True: "Yes", False: "No"})
    return display_df


def create_column_defs(df):
    return [
        {"name": column.replace("_", " ").title(), "id": column}
        for column in df.columns
    ]


def create_kpi_card(title, value, color, icon="bi-graph-up", trend=None):
    trend_badge = None
    if trend:
        trend_badge = html.Div(
            [
                html.I(className="bi bi-arrow-up-right me-1"),
                html.Span(trend)
            ],
            className="kpi-trend"
        )

    return dbc.Card(
        dbc.CardBody([
            html.Div([
                html.I(className=f"bi {icon} kpi-icon"),
                html.H6(title, className="kpi-title")
            ], className="kpi-card-top"),
            html.H4(value, className="kpi-value fw-bold"),
            trend_badge
        ], className="kpi-card-body p-3"),
        color=color,
        inverse=True,
        className="kpi-card h-100 shadow-sm"
    )


def create_insight_card(title, value, detail, icon, color_class):
    return dbc.Card(
        dbc.CardBody([
            html.Div([
                html.I(className=f"bi {icon} insight-icon {color_class}"),
                html.Div([
                    html.H6(title, className="insight-title"),
                    html.H4(value, className="insight-value"),
                    html.P(detail, className="insight-detail")
                ])
            ], className="insight-content")
        ]),
        className="insight-card h-100"
    )


def data_table(data, columns, page_size=15):
    return dash_table.DataTable(
        data=data,
        columns=columns,
        page_size=page_size,
        page_action="native",
        sort_action="native",
        filter_action="native",
        export_format="csv",
        export_headers="display",
        style_table={"overflowX": "auto"},
        style_cell={
            "textAlign": "left",
            "padding": "11px",
            "backgroundColor": "#101820",
            "color": "#f8f9fa",
            "border": "1px solid #263544",
            "minWidth": "120px",
            "fontFamily": "Inter, Segoe UI, Arial, sans-serif"
        },
        style_header={
            "backgroundColor": "#18232e",
            "color": "#ffffff",
            "fontWeight": "700",
            "padding": "12px",
            "border": "1px solid #30445a"
        },
        style_filter={
            "backgroundColor": "#0b1117",
            "color": "#ffffff",
            "border": "1px solid #30445a"
        },
        style_data_conditional=[
            {
                "if": {"filter_query": "{churn} = 1"},
                "backgroundColor": "#35151d",
                "color": "#fff2f4"
            },
            {
                "if": {"filter_query": "{high_loan_customer} = Yes"},
                "backgroundColor": "#33260d",
                "color": "#fff8e1"
            },
            {
                "if": {"filter_query": "{risk_segment} = High"},
                "borderLeft": "4px solid #ef476f"
            },
            {
                "if": {"filter_query": "{high_value_customer} = Yes"},
                "borderLeft": "4px solid #80ed99"
            }
        ]
    )


def create_modal_table(df):
    display_df = format_table_df(df)
    return data_table(
        display_df.to_dict("records"),
        create_column_defs(display_df),
        page_size=12
    )


def get_kpi_modal_config(clicked_id, df):
    modal_config = {
        "customer-kpi": {
            "title": "Customer Details",
            "summary": f"{len(df):,} customers match the current filters.",
            "df": df.sort_values("customer_id"),
            "columns": [
                "customer_id", "customer_name", "age", "gender", "state", "city",
                "branch_name", "occupation", "account_type", "balance",
                "loan_amount", "revenue", "credit_score", "risk_score",
                "risk_segment", "high_value_customer", "high_loan_customer", "is_active", "churn"
            ]
        },
        "deposit-kpi": {
            "title": "Deposit Details",
            "summary": f"Total deposits: {format_currency(df['balance'].sum())}",
            "df": df.sort_values("balance", ascending=False),
            "columns": [
                "customer_id", "customer_name", "state", "branch_name",
                "account_type", "balance", "monthly_income", "transaction_count",
                "deposit_to_loan_ratio", "is_active"
            ]
        },
        "loan-kpi": {
            "title": "Loan Details",
            "summary": f"Total loans: {format_currency(df['loan_amount'].sum())}",
            "df": df[df["loan_amount"] > 0].sort_values("loan_amount", ascending=False),
            "columns": [
                "customer_id", "customer_name", "state", "account_type",
                "loan_amount", "monthly_income", "loan_to_income_ratio",
                "credit_score", "risk_segment", "high_loan_customer", "churn"
            ]
        },
        "revenue-kpi": {
            "title": "Revenue Details",
            "summary": f"Total revenue: {format_currency(df['revenue'].sum())}",
            "df": df.sort_values("revenue", ascending=False),
            "columns": [
                "customer_id", "customer_name", "state", "account_type",
                "revenue", "balance", "transaction_count",
                "high_value_customer", "is_active"
            ]
        },
        "churn-kpi": {
            "title": "Churned Customer Details",
            "summary": f"{int(df['churn'].sum()):,} customers are marked as churned.",
            "df": df[df["churn"] == 1].sort_values("risk_score", ascending=False),
            "columns": [
                "customer_id", "customer_name", "age", "gender", "state",
                "account_type", "balance", "loan_amount", "revenue",
                "credit_score", "risk_score", "risk_segment"
            ]
        },
        "active-kpi": {
            "title": "Active Customer Details",
            "summary": f"{len(df[df['is_active'] == 'Active']):,} customers have active account status.",
            "df": df[df["is_active"] == "Active"].sort_values("customer_id"),
            "columns": [
                "customer_id", "customer_name", "age", "gender", "state",
                "account_type", "balance", "loan_amount", "revenue",
                "credit_score", "risk_score", "high_value_customer"
            ]
        },
        "risk-kpi": {
            "title": "Risk Score Details",
            "summary": f"Average customer risk score: {df['risk_score'].mean():.1f}",
            "df": df.sort_values("risk_score", ascending=False),
            "columns": [
                "customer_id", "customer_name", "state", "branch_name",
                "credit_score", "loan_to_income_ratio", "balance",
                "loan_amount", "risk_score", "risk_segment", "high_loan_customer", "churn"
            ]
        },
        "value-kpi": {
            "title": "High-Value Customer Details",
            "summary": f"{len(df[df['high_value_customer'] == 'Yes']):,} high-value customers match the filters.",
            "df": df[df["high_value_customer"] == "Yes"].sort_values("revenue", ascending=False),
            "columns": [
                "customer_id", "customer_name", "state", "branch_name",
                "account_type", "balance", "revenue", "monthly_income",
                "has_credit_card", "has_fixed_deposit", "high_value_customer"
            ]
        }
    }

    return modal_config.get(clicked_id)


def create_kpi_modal_body(config, search_enabled=False, customer_search=None):
    table_df = config["df"][config["columns"]]
    total_records = len(table_df)
    search_value = str(customer_search).strip() if customer_search else ""

    if search_enabled and search_value:
        table_df = table_df[
            table_df["customer_id"].astype(str).str.contains(search_value, case=False, na=False)
        ]

    showing_text = f"Showing {len(table_df):,} records based on the current filters."
    if search_enabled and search_value:
        showing_text = (
            f"Showing {len(table_df):,} matching records "
            f"from {total_records:,} filtered records."
        )

    return [
        html.P(config["summary"], className="fs-5 mb-2"),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Switch(
                        id="kpi-search-toggle",
                        label="Search customer ID",
                        value=bool(search_enabled),
                        className="mb-2"
                    ),
                    xs=12,
                    md=4
                ),
                dbc.Col(
                    dbc.Collapse(
                        dbc.Input(
                            id="kpi-customer-search",
                            type="text",
                            placeholder="Enter customer ID...",
                            value=search_value,
                            debounce=False,
                            className="form-control-sm"
                        ),
                        is_open=bool(search_enabled)
                    ),
                    xs=12,
                    md=8
                )
            ],
            className="g-3 align-items-center mb-3"
        ),
        html.P(showing_text, className="text-muted mb-4"),
        create_modal_table(table_df)
    ]
