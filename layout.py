from dash import html, dcc
import dash_bootstrap_components as dbc

from data import ACCOUNT_TYPES, GENDERS, STATES


def chart_panel(title, graph_id):
    return dbc.Card([
        dbc.CardHeader(title, className="panel-header fs-5 px-3 py-2"),
        dbc.CardBody([
            dcc.Loading(
                dcc.Graph(id=graph_id, style={"height": "360px"}),
                type="circle",
                color="#4cc9f0"
            )
        ], className="chart-body p-3")
    ], className="panel-card h-100 shadow-sm")


def kpi_target(kpi_id, title):
    return dbc.Col(
        html.Div(
            id=kpi_id,
            n_clicks=0,
            role="button",
            title=title,
            className="kpi-click-target h-100"
        ),
        xs=12,
        sm=6,
        lg=3,
        xl=3
    )


def create_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.P("CSV-backed portfolio dashboard", className="eyebrow mb-1"),
                    html.H1(
                        "Bank Customer Analytics Dashboard",
                        className="dashboard-title text-info mb-2"
                    ),
                    html.P(
                        "Customer, branch, product, risk, churn, loan, deposit, and transaction analytics.",
                        className="dashboard-subtitle mb-0"
                    )
                ], className="page-heading")
            ])
        ], className="mb-4"),

        dbc.Row([
            dbc.Col([
                html.Label("Select State", className="filter-label mb-2"),
                dcc.Dropdown(
                    id="state-filter",
                    options=[{"label": i, "value": i} for i in STATES],
                    multi=True,
                    placeholder="Select states",
                    className="filter-dropdown"
                )
            ], xs=12, md=6, xl=3),

            dbc.Col([
                html.Label("Account Type", className="filter-label mb-2"),
                dcc.Dropdown(
                    id="account-filter",
                    options=[{"label": i, "value": i} for i in ACCOUNT_TYPES],
                    multi=True,
                    placeholder="Select account types",
                    className="filter-dropdown"
                )
            ], xs=12, md=6, xl=3),

            dbc.Col([
                html.Label("Gender", className="filter-label mb-2"),
                dcc.Dropdown(
                    id="gender-filter",
                    options=[{"label": i, "value": i} for i in GENDERS],
                    multi=True,
                    placeholder="Select gender",
                    className="filter-dropdown"
                )
            ], xs=12, md=4, xl=2),

            dbc.Col([
                html.Label("Age Range", className="filter-label mb-2"),
                html.Div([
                    dbc.Input(
                        id="age-min-input",
                        type="number",
                        min=18,
                        max=70,
                        step=1,
                        value=18,
                        className="age-value-input",
                        debounce=False
                    ),
                    html.Div(
                        dcc.RangeSlider(
                            id="age-slider",
                            min=18,
                            max=70,
                            value=[18, 70],
                            marks={
                                18: {"label": "18", "style": {"color": "#f8f9fa", "fontWeight": "700"}},
                                30: {"label": "30", "style": {"color": "#cbd5e1", "fontWeight": "700"}},
                                50: {"label": "50", "style": {"color": "#cbd5e1", "fontWeight": "700"}},
                                70: {"label": "70", "style": {"color": "#f8f9fa", "fontWeight": "700"}},
                            },
                            tooltip={
                                "always_visible": False,
                                "placement": "bottom",
                                "style": {"display": "none"},
                            },
                            allowCross=False,
                            className="age-range-slider"
                        ),
                        className="age-slider-wrap"
                    ),
                    dbc.Input(
                        id="age-max-input",
                        type="number",
                        min=18,
                        max=70,
                        step=1,
                        value=70,
                        className="age-value-input",
                        debounce=False
                    )
                ], className="age-range-control")
            ], xs=12, md=8, xl=4)
        ], className="filter-band g-3 align-items-end mb-4"),

        dbc.Row([
            kpi_target("customer-kpi", "Open Customers data"),
            kpi_target("deposit-kpi", "Open Deposits data"),
            kpi_target("loan-kpi", "Open Loans data"),
            kpi_target("revenue-kpi", "Open Revenue data"),
            kpi_target("churn-kpi", "Open Churn Rate data"),
            kpi_target("active-kpi", "Open Active data"),
            kpi_target("risk-kpi", "Open Risk Score data"),
            kpi_target("value-kpi", "Open High-Value Customer data"),
        ], className="g-3 mb-4 align-items-stretch"),

        dbc.Row(id="insight-cards", className="g-3 mb-4 align-items-stretch"),

        dbc.Row([
            dbc.Col(chart_panel("Customer Growth Trend", "growth-chart"), xs=12, lg=6),
            dbc.Col(chart_panel("Customer Segmentation", "segment-chart"), xs=12, lg=6)
        ], className="g-4 mb-4 align-items-stretch"),

        dbc.Row([
            dbc.Col(chart_panel("Revenue by Account Type", "revenue-chart"), xs=12, lg=6),
            dbc.Col(chart_panel("Customer Age Distribution", "age-chart"), xs=12, lg=6)
        ], className="g-4 mb-4 align-items-stretch"),

        dbc.Row([
            dbc.Col(chart_panel("Churn Risk Segments", "risk-chart"), xs=12, lg=6),
            dbc.Col(chart_panel("Top Branches by Revenue", "branch-chart"), xs=12, lg=6)
        ], className="g-4 mb-4 align-items-stretch"),

        dbc.Row([
            dbc.Col(chart_panel("Product Usage", "product-chart"), xs=12, lg=6),
            dbc.Col(chart_panel("Transaction Volume Trend", "transaction-chart"), xs=12, lg=6)
        ], className="g-4 mb-4 align-items-stretch"),

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
                        dcc.Loading(
                            html.Div(id="customer-table-container"),
                            type="circle",
                            color="#4cc9f0"
                        )
                    ], className="table-card-body")
                ], className="panel-card shadow-sm")
            ])
        ], className="g-4 mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Recent Transactions", className="panel-header fs-5 px-3 py-2"),
                    dbc.CardBody([
                        dcc.Loading(
                            html.Div(id="transaction-table-container"),
                            type="circle",
                            color="#4cc9f0"
                        )
                    ], className="table-card-body")
                ], className="panel-card shadow-sm")
            ])
        ], className="g-4 mb-4"),

        html.Footer([
            html.Span("Data source: local CSV files generated in the project data folder."),
            html.Span("Built with Dash, Plotly, Pandas, and Dash Bootstrap Components.")
        ], className="dashboard-footer"),

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
        ),

        dcc.Store(id="active-kpi-modal")
    ], fluid=True, className="dashboard-shell p-4")
