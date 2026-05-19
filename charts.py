import pandas as pd
import plotly.express as px


CHART_COLORS = ["#4cc9f0", "#80ed99", "#ffd166", "#ef476f", "#b8f2e6", "#f78c6b"]


def style_chart(fig):
    fig.update_layout(
        height=360,
        margin={"l": 40, "r": 20, "t": 24, "b": 48},
        paper_bgcolor="#101820",
        plot_bgcolor="#101820",
        font={"color": "#f8f9fa"},
        legend_title_text="",
        colorway=CHART_COLORS,
        hoverlabel={"bgcolor": "#18232e", "font_color": "#f8f9fa"}
    )
    fig.update_xaxes(gridcolor="#263544", zerolinecolor="#263544")
    fig.update_yaxes(gridcolor="#263544", zerolinecolor="#263544")
    return fig


def _empty_chart(message):
    fig = px.scatter(template="plotly_dark")
    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font={"size": 16, "color": "#cbd5e1"}
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return style_chart(fig)


def create_dashboard_figures(df, transactions):
    if df.empty:
        empty = _empty_chart("No data matches the current filters")
        return (empty, empty, empty, empty, empty, empty, empty, empty)

    growth_df = df.groupby("month").size().reset_index(name="customers")
    revenue_df = df.groupby("account_type", as_index=False)["revenue"].sum()
    risk_df = df.groupby("risk_segment", as_index=False).agg(
        customers=("customer_id", "count"),
        avg_risk=("risk_score", "mean")
    )
    branch_df = (
        df.groupby("branch_name", as_index=False)
        .agg(revenue=("revenue", "sum"), customers=("customer_id", "count"))
        .sort_values("revenue", ascending=False)
        .head(10)
    )
    product_df = pd.DataFrame({
        "product": ["Credit Card", "Loan", "Fixed Deposit", "Savings", "Current"],
        "customers": [
            int(df["has_credit_card"].sum()),
            int(df["has_active_loan"].sum()),
            int(df["has_fixed_deposit"].sum()),
            int(df["uses_savings"].sum()),
            int(df["uses_current"].sum())
        ]
    })
    transaction_df = (
        transactions.groupby("month", as_index=False)["amount"].sum()
        if not transactions.empty
        else pd.DataFrame({"month": [], "amount": []})
    )

    growth_fig = style_chart(px.line(
        growth_df,
        x="month",
        y="customers",
        markers=True,
        template="plotly_dark"
    ))

    segment_fig = style_chart(px.pie(
        df,
        names="account_type",
        hole=0.5,
        template="plotly_dark",
        color_discrete_sequence=CHART_COLORS
    ))

    revenue_fig = style_chart(px.bar(
        revenue_df,
        x="account_type",
        y="revenue",
        color="account_type",
        template="plotly_dark",
        color_discrete_sequence=CHART_COLORS
    ))
    revenue_fig.update_layout(showlegend=False)

    age_fig = style_chart(px.histogram(
        df,
        x="age",
        nbins=25,
        template="plotly_dark",
        color_discrete_sequence=["#4cc9f0"]
    ))

    risk_fig = style_chart(px.bar(
        risk_df,
        x="risk_segment",
        y="customers",
        color="risk_segment",
        text="customers",
        template="plotly_dark",
        category_orders={"risk_segment": ["Low", "Medium", "High"]},
        color_discrete_map={"Low": "#80ed99", "Medium": "#ffd166", "High": "#ef476f"}
    ))
    risk_fig.update_layout(showlegend=False)

    branch_fig = style_chart(px.bar(
        branch_df,
        x="revenue",
        y="branch_name",
        color="customers",
        orientation="h",
        template="plotly_dark",
        color_continuous_scale="Teal"
    ))
    branch_fig.update_layout(yaxis={"categoryorder": "total ascending"})

    product_fig = style_chart(px.bar(
        product_df,
        x="product",
        y="customers",
        color="product",
        text="customers",
        template="plotly_dark",
        color_discrete_sequence=CHART_COLORS
    ))
    product_fig.update_layout(showlegend=False)

    transaction_fig = style_chart(px.area(
        transaction_df,
        x="month",
        y="amount",
        template="plotly_dark",
        color_discrete_sequence=["#80ed99"]
    ))

    return (
        growth_fig,
        segment_fig,
        revenue_fig,
        age_fig,
        risk_fig,
        branch_fig,
        product_fig,
        transaction_fig
    )
