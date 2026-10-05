import os
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="E-Commerce Executive Command Center",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# ENVIRONMENT
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

load_dotenv(BASE_DIR / ".env")

API_BASE_URL = "http://127.0.0.1:8000"


# ============================================================
# DATABASE
# ============================================================

@st.cache_resource
def create_db_engine():

    required = [
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB",
    ]

    missing = [
        item
        for item in required
        if not os.getenv(item)
    ]

    if missing:
        raise RuntimeError(
            "Missing environment variables: "
            + ", ".join(missing)
        )

    user = quote_plus(os.getenv("POSTGRES_USER"))
    password = quote_plus(os.getenv("POSTGRES_PASSWORD"))
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    database = os.getenv("POSTGRES_DB")

    url = (
        "postgresql+psycopg2://"
        f"{user}:{password}"
        f"@{host}:{port}/{database}"
    )

    return create_engine(
        url,
        pool_pre_ping=True,
        pool_recycle=1800,
    )


try:
    engine = create_db_engine()

except Exception as exc:

    st.error("Database configuration error.")
    st.exception(exc)
    st.stop()


# ============================================================
# CSS
# ============================================================

st.html("""
<style>

:root {
    --bg: #0b1120;
    --surface: #111827;
    --surface-2: #172033;
    --surface-3: #1e293b;

    --border: #334155;

    --text: #f8fafc;
    --text-secondary: #cbd5e1;
    --text-muted: #94a3b8;

    --accent: #38bdf8;
    --accent-soft: rgba(56, 189, 248, 0.12);

    --green: #34d399;
    --green-soft: rgba(52, 211, 153, 0.12);

    --red: #fb7185;
    --red-soft: rgba(251, 113, 133, 0.12);

    --yellow: #fbbf24;
    --yellow-soft: rgba(251, 191, 36, 0.12);
}


/* =========================
   MAIN APPLICATION
   ========================= */

.stApp {
    background: var(--bg);
    color: var(--text);
}

.main {
    background: var(--bg);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}


/* =========================
   GENERAL TEXT
   ========================= */

h1, h2, h3, h4, h5, h6 {
    color: var(--text) !important;
}

p, span, div {
    color: inherit;
}

.stMarkdown {
    color: var(--text-secondary);
}

label {
    color: var(--text-secondary) !important;
}


/* =========================
   SIDEBAR
   ========================= */

section[data-testid="stSidebar"] {
    background: #0a0f1c;
    border-right: 1px solid var(--border);
}

section[data-testid="stSidebar"] * {
    color: var(--text-secondary);
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: var(--text) !important;
}


/* =========================
   EXECUTIVE HEADER
   ========================= */

.exec-title {
    font-size: 30px;
    font-weight: 750;
    color: var(--text);
    margin-bottom: 4px;
}

.exec-subtitle {
    font-size: 14px;
    color: var(--text-muted);
    margin-bottom: 24px;
}


/* =========================
   SECTION HEADERS
   ========================= */

.section-title {
    font-size: 20px;
    font-weight: 700;
    color: var(--text);
    margin-top: 24px;
    margin-bottom: 5px;
}

.section-subtitle {
    font-size: 13px;
    color: var(--text-muted);
    margin-bottom: 15px;
}


/* =========================
   CARDS
   ========================= */

.metric-card,
.signal-card,
.driver-card,
.action-card,
.target-card,
.risk-card,
.growth-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px;
    color: var(--text);
}

.metric-card:hover,
.signal-card:hover,
.driver-card:hover,
.action-card:hover,
.target-card:hover,
.risk-card:hover,
.growth-card:hover {
    border-color: #475569;
}


/* =========================
   KPI LABELS
   ========================= */

.metric-label {
    color: var(--text-muted) !important;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.metric-value {
    color: var(--text) !important;
    font-size: 27px;
    font-weight: 750;
    margin-top: 6px;
}

.metric-change {
    font-size: 13px;
    font-weight: 650;
    margin-top: 5px;
}

.metric-change.positive {
    color: var(--green) !important;
}

.metric-change.negative {
    color: var(--red) !important;
}

.metric-change.neutral {
    color: var(--text-muted) !important;
}


/* =========================
   EXECUTIVE BRIEF
   ========================= */

.brief-card {
    background: linear-gradient(
        135deg,
        #111827 0%,
        #172033 100%
    );

    border: 1px solid #334155;
    border-radius: 14px;

    padding: 22px;
    margin-bottom: 18px;
}

.signal-label {
    color: var(--accent) !important;
    font-size: 11px;
    font-weight: 750;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
}

.brief-title {
    color: var(--text) !important;
    font-size: 21px;
    font-weight: 700;
    margin-bottom: 8px;
}

.brief-text {
    color: var(--text-secondary) !important;
    font-size: 14px;
    line-height: 1.6;
}


/* =========================
   TARGET POSITION
   ========================= */

.target-card {
    background: var(--surface);
}

.target-name {
    color: var(--text-secondary) !important;
    font-size: 13px;
    font-weight: 650;
}

.target-value {
    color: var(--text) !important;
    font-size: 23px;
    font-weight: 750;
}

.target-label {
    color: var(--text-muted) !important;
    font-size: 11px;
}

.target-gap-positive {
    color: var(--green) !important;
    font-weight: 700;
}

.target-gap-negative {
    color: var(--red) !important;
    font-weight: 700;
}


/* =========================
   EXECUTIVE SIGNAL
   ========================= */

.signal-card {
    background: #121a2a;
    border-left: 4px solid var(--accent);
}

.signal-title {
    color: var(--text) !important;
    font-size: 17px;
    font-weight: 700;
}

.signal-body {
    color: var(--text-secondary) !important;
    font-size: 13px;
    line-height: 1.55;
}


/* =========================
   DRIVER CARDS
   ========================= */

.driver-card {
    background: var(--surface);
}

.driver-rank {
    color: var(--accent) !important;
    font-size: 11px;
    font-weight: 750;
    text-transform: uppercase;
}

.driver-title {
    color: var(--text) !important;
    font-size: 16px;
    font-weight: 700;
    margin-top: 5px;
}

.driver-evidence {
    color: var(--text-secondary) !important;
    font-size: 13px;
    line-height: 1.55;
    margin-top: 8px;
}

.driver-impact {
    color: var(--red) !important;
    font-size: 16px;
    font-weight: 750;
    margin-top: 10px;
}


/* =========================
   ACTION PLAN
   ========================= */

.action-card {
    background: #111827;
}

.action-priority {
    color: var(--yellow) !important;
    font-size: 11px;
    font-weight: 750;
    text-transform: uppercase;
}

.action-title {
    color: var(--text) !important;
    font-size: 15px;
    font-weight: 700;
    margin-top: 5px;
}

.action-reason {
    color: var(--text-secondary) !important;
    font-size: 13px;
    line-height: 1.5;
    margin-top: 6px;
}

.action-meta {
    color: var(--text-muted) !important;
    font-size: 11px;
    margin-top: 10px;
}


/* =========================
   GROWTH OPPORTUNITY
   ========================= */

.growth-card {
    background: #101b1a;
    border-left: 4px solid var(--green);
}

.growth-title {
    color: var(--text) !important;
    font-size: 16px;
    font-weight: 700;
}

.growth-body {
    color: var(--text-secondary) !important;
    font-size: 13px;
    line-height: 1.5;
}


/* =========================
   RISK RADAR
   ========================= */

.risk-card {
    background: #1b1418;
    border-left: 4px solid var(--red);
}

.risk-title {
    color: var(--text) !important;
    font-size: 15px;
    font-weight: 700;
}

.risk-body {
    color: var(--text-secondary) !important;
    font-size: 13px;
    line-height: 1.5;
}


/* =========================
   STREAMLIT DATAFRAMES
   ========================= */

[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
}


/* =========================
   STREAMLIT ALERTS
   ========================= */

[data-testid="stAlert"] {
    background: var(--surface-2);
    border: 1px solid var(--border);
    color: var(--text-secondary);
}


/* =========================
   BUTTONS
   ========================= */

.stButton > button {
    background: var(--surface-2);
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 8px;
}

.stButton > button:hover {
    background: var(--surface-3);
    border-color: #64748b;
}


/* =========================
   INPUTS
   ========================= */

.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    background: var(--surface) !important;
    color: var(--text) !important;
    border-color: var(--border) !important;
}


/* =========================
   DIVIDERS
   ========================= */

hr {
    border-color: var(--border) !important;
}


/* =========================
   CHART AREA
   ========================= */

[data-testid="stVegaLiteChart"],
[data-testid="stArrowVegaLiteChart"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 8px;
}


/* =========================
   PLOTLY
   ========================= */

.js-plotly-plot {
    background: var(--surface) !important;
    border-radius: 12px;
}


/* =========================
   FOOTER
   ========================= */

.dashboard-footer {
    color: var(--text-muted) !important;
    font-size: 11px;
    text-align: center;
    margin-top: 35px;
    padding-top: 20px;
    border-top: 1px solid var(--border);
}

</style>
""")


# ============================================================
# HELPERS
# ============================================================

def read_sql(query, params=None):
    return pd.read_sql(
        text(query),
        engine,
        params=params or {},
    )


def safe_float(value):

    try:
        if pd.isna(value):
            return 0.0

        return float(value)

    except Exception:
        return 0.0


def percentage_change(current, previous):

    if previous == 0:
        return 0.0

    return (
        (current - previous)
        / abs(previous)
        * 100
    )


def format_lakh(value):
    return f"₹{safe_float(value) / 100000:.2f}L"


def format_rupees(value):
    return f"₹{safe_float(value):,.0f}"


def format_metric_value(metric, value):

    value = safe_float(value)

    if metric in {"revenue", "profit"}:
        return format_lakh(value)

    if metric == "roas":
        return f"{value:.2f}x"

    if metric == "conversion_rate":
        return f"{value:.2f}%"

    if metric == "cac":
        return format_rupees(value)

    return f"{value:,.0f}"


def section_title(title, description=None):

    st.html(
        f"""
        <div class="section-label">
            {title}
        </div>
        """
    )

    if description:

        st.html(
            f"""
            <div class="section-description">
                {description}
            </div>
            """
        )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.html(
        """
        <div style="
            font-size:0.7rem;
            font-weight:800;
            letter-spacing:0.12em;
            color:#9ca3af;
            text-transform:uppercase;
            margin-bottom:0.5rem;
        ">
            E-COMMERCE BI
        </div>

        <div style="
            font-size:1.25rem;
            font-weight:800;
            color:#ffffff;
            margin-bottom:1.5rem;
        ">
            Executive Command Center
        </div>
        """
    )

    st.html(
        """
        <div style="
            font-size:0.7rem;
            font-weight:800;
            color:#9ca3af;
            letter-spacing:0.1em;
            text-transform:uppercase;
            margin-bottom:0.5rem;
        ">
            Dashboard Period
        </div>
        """
    )

    start_date = st.date_input(
        "Start Date",
        value=date(2026, 9, 1),
        key="dashboard_start_date",
    )

    end_date = st.date_input(
        "End Date",
        value=date(2026, 9, 30),
        key="dashboard_end_date",
    )

    st.caption(
        "All executive metrics are recalculated "
        "for the selected period."
    )

    st.markdown("---")

    st.html(
        """
        <div style="
            color:#6b7280;
            font-size:0.68rem;
            font-weight:800;
            letter-spacing:0.1em;
            text-transform:uppercase;
        ">
            Decision Flow
        </div>

        <div style="
            color:#d1d5db;
            font-size:0.78rem;
            line-height:1.9;
            margin-top:0.5rem;
        ">
            SEE → Understand → ACT
        </div>
        """
    )


if end_date < start_date:

    st.error(
        "End date must be greater than or equal to start date."
    )

    st.stop()


# ============================================================
# PERIODS
# ============================================================

period_days = (
    end_date - start_date
).days + 1

previous_end = start_date - timedelta(days=1)

previous_start = (
    previous_end
    - timedelta(days=period_days - 1)
)

period_label = (
    f"{start_date.strftime('%d %b %Y')}"
    f" – "
    f"{end_date.strftime('%d %b %Y')}"
)


# ============================================================
# HEADER
# ============================================================

st.html(
    """
    <div class="executive-eyebrow">
        Executive Decision Support
    </div>
    """
)

st.html(
    """
    <div class="hero-title">
        E-Commerce Executive Command Center
    </div>
    """
)

st.html(
    f"""
    <div class="hero-subtitle">
        {period_label}
        &nbsp;·&nbsp;
        India Online Retail
        &nbsp;·&nbsp;
        Executive View
    </div>
    """
)


# ============================================================
# 1. BUSINESS HEALTH
# ============================================================

current_query = """
SELECT
    COALESCE(SUM(oi.revenue), 0) AS revenue,
    COALESCE(SUM(oi.profit), 0) AS profit,
    COUNT(DISTINCT o.order_id) AS orders,
    COUNT(DISTINCT o.customer_id) AS customers
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
WHERE o.order_status = 'Delivered'
  AND o.order_date >= :start_date
  AND o.order_date < (
      :end_date + INTERVAL '1 day'
  )
"""


previous_query = """
SELECT
    COALESCE(SUM(oi.revenue), 0) AS revenue,
    COALESCE(SUM(oi.profit), 0) AS profit,
    COUNT(DISTINCT o.order_id) AS orders,
    COUNT(DISTINCT o.customer_id) AS customers
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
WHERE o.order_status = 'Delivered'
  AND o.order_date >= :start_date
  AND o.order_date < (
      :end_date + INTERVAL '1 day'
  )
"""


try:

    current = read_sql(
        current_query,
        {
            "start_date": start_date,
            "end_date": end_date,
        },
    ).iloc[0]

    previous = read_sql(
        previous_query,
        {
            "start_date": previous_start,
            "end_date": previous_end,
        },
    ).iloc[0]

except Exception as exc:

    st.error("Unable to load business data.")
    st.exception(exc)
    st.stop()


revenue = safe_float(current["revenue"])
profit = safe_float(current["profit"])
orders = int(current["orders"])
customers = int(current["customers"])

previous_revenue = safe_float(previous["revenue"])
previous_profit = safe_float(previous["profit"])
previous_orders = int(previous["orders"])
previous_customers = int(previous["customers"])

revenue_change = percentage_change(
    revenue,
    previous_revenue,
)

profit_change = percentage_change(
    profit,
    previous_profit,
)

orders_change = percentage_change(
    orders,
    previous_orders,
)

customer_change = percentage_change(
    customers,
    previous_customers,
)

profit_margin = (
    profit / revenue * 100
    if revenue
    else 0
)

previous_margin = (
    previous_profit / previous_revenue * 100
    if previous_revenue
    else 0
)

margin_change = (
    profit_margin
    - previous_margin
)


section_title("Business Health")

kpi1, kpi2, kpi3, kpi4 = st.columns(
    4,
    gap="medium",
)

with kpi1:

    st.metric(
        "Revenue",
        format_lakh(revenue),
        f"{revenue_change:+.2f}%",
    )

with kpi2:

    st.metric(
        "Profit",
        format_lakh(profit),
        f"{profit_change:+.2f}%",
    )

with kpi3:

    st.metric(
        "Profit Margin",
        f"{profit_margin:.2f}%",
        f"{margin_change:+.2f} pp",
    )

with kpi4:

    st.metric(
        "Orders",
        f"{orders:,}",
        f"{orders_change:+.2f}%",
    )


# ============================================================
# 2. CATEGORY ANALYSIS
# ============================================================

category_query = """
WITH current_period AS (

    SELECT
        p.category,
        SUM(oi.revenue) AS revenue,
        SUM(oi.profit) AS profit,
        SUM(
            oi.unit_price
            * oi.quantity
            * oi.discount_percent
            / 100
        ) AS discounts

    FROM order_items oi

    JOIN orders o
        ON oi.order_id = o.order_id

    JOIN products p
        ON oi.product_id = p.product_id

    WHERE o.order_status = 'Delivered'
      AND o.order_date >= :current_start
      AND o.order_date <= :current_end

    GROUP BY p.category
),

previous_period AS (

    SELECT
        p.category,
        SUM(oi.revenue) AS revenue,
        SUM(oi.profit) AS profit,
        SUM(
            oi.unit_price
            * oi.quantity
            * oi.discount_percent
            / 100
        ) AS discounts

    FROM order_items oi

    JOIN orders o
        ON oi.order_id = o.order_id

    JOIN products p
        ON oi.product_id = p.product_id

    WHERE o.order_status = 'Delivered'
      AND o.order_date >= :previous_start
      AND o.order_date <= :previous_end

    GROUP BY p.category
),

current_returns AS (

    SELECT
        p.category,
        SUM(r.refund_amount) AS returns

    FROM returns r

    JOIN products p
        ON r.product_id = p.product_id

    WHERE r.return_date >= :current_start
      AND r.return_date <= :current_end

    GROUP BY p.category
),

previous_returns AS (

    SELECT
        p.category,
        SUM(r.refund_amount) AS returns

    FROM returns r

    JOIN products p
        ON r.product_id = p.product_id

    WHERE r.return_date >= :previous_start
      AND r.return_date <= :previous_end

    GROUP BY p.category
)

SELECT

    COALESCE(
        c.category,
        p.category
    ) AS category,

    COALESCE(c.revenue, 0)
        AS current_revenue,

    COALESCE(p.revenue, 0)
        AS previous_revenue,

    COALESCE(c.profit, 0)
        AS current_profit,

    COALESCE(p.profit, 0)
        AS previous_profit,

    COALESCE(c.discounts, 0)
        AS current_discounts,

    COALESCE(p.discounts, 0)
        AS previous_discounts,

    COALESCE(cr.returns, 0)
        AS current_returns,

    COALESCE(pr.returns, 0)
        AS previous_returns

FROM current_period c

FULL OUTER JOIN previous_period p
    ON c.category = p.category

LEFT JOIN current_returns cr
    ON COALESCE(
        c.category,
        p.category
    ) = cr.category

LEFT JOIN previous_returns pr
    ON COALESCE(
        c.category,
        p.category
    ) = pr.category

ORDER BY
    COALESCE(
        c.category,
        p.category
    )
"""


try:

    categories = read_sql(
        category_query,
        {
            "current_start": start_date,
            "current_end": end_date,
            "previous_start": previous_start,
            "previous_end": previous_end,
        },
    )

except Exception as exc:

    st.error("Unable to load category analysis.")
    st.exception(exc)
    st.stop()


if not categories.empty:

    categories["profit_change"] = (
        categories["current_profit"]
        - categories["previous_profit"]
    )

    categories["profit_change_percent"] = (
        (
            categories["current_profit"]
            - categories["previous_profit"]
        )
        /
        categories["previous_profit"]
        .abs()
        .replace(0, pd.NA)
        * 100
    ).fillna(0)

    categories["revenue_change_percent"] = (
        (
            categories["current_revenue"]
            - categories["previous_revenue"]
        )
        /
        categories["previous_revenue"]
        .abs()
        .replace(0, pd.NA)
        * 100
    ).fillna(0)

    current_margin = (
        categories["current_profit"]
        /
        categories["current_revenue"]
        .replace(0, pd.NA)
        * 100
    )

    previous_margin_cat = (
        categories["previous_profit"]
        /
        categories["previous_revenue"]
        .replace(0, pd.NA)
        * 100
    )

    categories["margin_change"] = (
        current_margin
        - previous_margin_cat
    ).fillna(0)

    current_return_rate = (
        categories["current_returns"]
        /
        categories["current_revenue"]
        .replace(0, pd.NA)
        * 100
    )

    previous_return_rate = (
        categories["previous_returns"]
        /
        categories["previous_revenue"]
        .replace(0, pd.NA)
        * 100
    )

    categories["return_rate_change"] = (
        current_return_rate
        - previous_return_rate
    ).fillna(0)

    current_discount_rate = (
        categories["current_discounts"]
        /
        categories["current_revenue"]
        .replace(0, pd.NA)
        * 100
    )

    previous_discount_rate = (
        categories["previous_discounts"]
        /
        categories["previous_revenue"]
        .replace(0, pd.NA)
        * 100
    )

    categories["discount_rate_change"] = (
        current_discount_rate
        - previous_discount_rate
    ).fillna(0)

    categories = categories.fillna(0)

else:

    categories = pd.DataFrame()


declining = (
    categories[
        categories["profit_change"] < 0
    ]
    .sort_values("profit_change")
) if not categories.empty else pd.DataFrame()


growing = (
    categories[
        categories["profit_change"] > 0
    ]
    .sort_values(
        "profit_change",
        ascending=False,
    )
) if not categories.empty else pd.DataFrame()


# ============================================================
# 3. EXECUTIVE BRIEF
# ============================================================

section_title("Executive Brief")


if (
    profit_change < 0
    and not declining.empty
):

    largest = declining.iloc[0]

    brief_text = (
        f"Profit declined "
        f"{abs(profit_change):.2f}% "
        f"to {format_lakh(profit)}. "
        f"{largest['category']} created the "
        f"largest identified category-level "
        f"pressure at "
        f"{format_rupees(abs(largest['profit_change']))}."
    )

    if not growing.empty:

        strongest = growing.iloc[0]

        brief_text += (
            f" {strongest['category']} partially "
            f"offset the decline with profit growth "
            f"of "
            f"{strongest['profit_change_percent']:.2f}%."
        )

elif profit_change >= 0:

    brief_text = (
        f"Profit increased "
        f"{profit_change:.2f}% "
        f"to {format_lakh(profit)}."
    )

    if not growing.empty:

        strongest = growing.iloc[0]

        brief_text += (
            f" {strongest['category']} is the "
            f"strongest positive category."
        )

else:

    brief_text = (
        f"Current profit is "
        f"{format_lakh(profit)}."
    )


st.html(
    f"""
    <div class="signal-card {'positive' if profit_change >= 0 else ''}">

        <div class="signal-label">
            What Management Should Know
        </div>

        <div class="signal-detail">
            {brief_text}
        </div>

    </div>
    """
)


# ============================================================
# 4. TARGET POSITION
# ============================================================

section_title(
    "Target Position",
    "Actual performance against the monthly business targets.",
)


try:

    target_df = read_sql(
        """
        SELECT
            month,
            revenue_target,
            profit_target,
            orders_target,
            customer_target
        FROM targets
        ORDER BY month
        """
    )

except Exception:

    target_df = pd.DataFrame()


target_row = None


if not target_df.empty:

    target_df["month_parsed"] = pd.to_datetime(
        target_df["month"],
        errors="coerce",
    )

    target_month = target_df[
        (
            target_df["month_parsed"].dt.month
            == start_date.month
        )
        &
        (
            target_df["month_parsed"].dt.year
            == start_date.year
        )
    ]

    if not target_month.empty:

        target_row = target_month.iloc[0]


if target_row is not None:

    target_records = [

        (
            "Revenue",
            revenue,
            safe_float(
                target_row["revenue_target"]
            ),
        ),

        (
            "Profit",
            profit,
            safe_float(
                target_row["profit_target"]
            ),
        ),

        (
            "Orders",
            orders,
            safe_float(
                target_row["orders_target"]
            ),
        ),

        (
            "Customers",
            customers,
            safe_float(
                target_row["customer_target"]
            ),
        ),
    ]

    target_cols = st.columns(
        4,
        gap="medium",
    )

    for col, (
        metric,
        actual,
        target,
    ) in zip(
        target_cols,
        target_records,
    ):

        achievement = (
            actual / target * 100
            if target
            else 0
        )

        gap = actual - target

        if metric in {
            "Revenue",
            "Profit",
        }:

            actual_text = (
                f"₹{actual / 100000:.2f}L"
            )

            target_text = (
                f"₹{target / 100000:.2f}L"
            )

            gap_text = (
                f"₹{gap / 100000:+.2f}L"
            )

        else:

            actual_text = f"{int(actual):,}"
            target_text = f"{int(target):,}"
            gap_text = f"{int(gap):+,}"

        progress = max(
            0,
            min(achievement, 100),
        )

        with col:

            st.html(
                f"""
                <div class="target-card">

                    <div class="target-name">
                        {metric}
                    </div>

                    <div class="target-value">
                        {actual_text}
                    </div>

                    <div class="target-achievement">
                        {achievement:.1f}% of target
                    </div>

                    <div class="target-bar">
                        <div
                            class="target-fill"
                            style="width:{progress:.1f}%"
                        ></div>
                    </div>

                    <div class="target-gap">
                        Target {target_text}
                        &nbsp;·&nbsp;
                        Gap {gap_text}
                    </div>

                </div>
                """
            )

    revenue_target = target_records[0][2]
    profit_target = target_records[1][2]

    revenue_achievement = (
        revenue / revenue_target * 100
        if revenue_target
        else 0
    )

    profit_achievement = (
        profit / profit_target * 100
        if profit_target
        else 0
    )

    if (
        revenue_achievement < 100
        and profit_achievement >= 100
    ):

        st.info(
            "Revenue is below target while profit is above "
            "target. Profit performance is currently stronger "
            "than sales-volume performance."
        )


# ============================================================
# 5. EXECUTIVE SIGNAL
# ============================================================

section_title("Executive Signal")


if profit_change < 0:

    primary_pressure = (
        declining.iloc[0]["category"]
        if not declining.empty
        else "Multiple categories"
    )

    impact = (
        abs(declining.iloc[0]["profit_change"])
        if not declining.empty
        else 0
    )

    movement = profit - previous_profit

    st.html(
        f"""
        <div class="signal-card">

            <div class="signal-label">
                Attention Required
            </div>

            <div class="signal-title">
                Profit declined {abs(profit_change):.2f}%
            </div>

            <div class="signal-detail">
                Current profit:
                <strong>{format_lakh(profit)}</strong>
                <br><br>

                Movement versus previous comparable period:
                <strong>{format_rupees(movement)}</strong>
                <br><br>

                Primary identified category pressure:
                <strong>{primary_pressure}</strong>
                with approximately
                <strong>{format_rupees(impact)}</strong>
                in identified profit impact.
            </div>

        </div>
        """
    )

else:

    st.html(
        f"""
        <div class="signal-card positive">

            <div class="signal-label">
                Positive Movement
            </div>

            <div class="signal-title">
                Profit increased {profit_change:.2f}%
            </div>

            <div class="signal-detail">
                Current profit:
                <strong>{format_lakh(profit)}</strong>
            </div>

        </div>
        """
    )


# ============================================================
# 6. PROFIT IMPACT
# ============================================================

section_title(
    "Profit Impact",
    "Category-level contribution to the change in profit.",
)


if not categories.empty:

    impact_df = categories[
        [
            "category",
            "profit_change",
        ]
    ].copy()

    impact_df = impact_df.sort_values(
        "profit_change"
    )

    impact_fig = go.Figure()

    impact_fig.add_trace(
        go.Bar(
            x=impact_df["profit_change"],
            y=impact_df["category"],
            orientation="h",
            text=[
                format_rupees(
                    abs(value)
                )
                for value
                in impact_df["profit_change"]
            ],
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "%{y}"
                "<br>Profit change: ₹%{x:,.0f}"
                "<extra></extra>"
            ),
        )
    )

    impact_fig.add_vline(
        x=0,
        line_width=1,
    )

    impact_fig.update_layout(
        height=360,
        margin=dict(
            l=10,
            r=60,
            t=20,
            b=20,
        ),
        template="plotly_white",
        showlegend=False,
        xaxis_title=None,
        yaxis_title=None,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter, Arial, sans-serif",
            color="#374151",
        ),
    )

    st.plotly_chart(
        impact_fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )


# ============================================================
# 7. WHY DID PROFIT CHANGE?
# ============================================================

section_title(
    "Why Did Profit Change?",
    "The three largest identified category-level pressures.",
)


negative = (
    categories[
        categories["profit_change"] < 0
    ]
    .sort_values(
        "profit_change"
    )
    .head(3)
) if not categories.empty else pd.DataFrame()


if not negative.empty:

    driver_cols = st.columns(
        len(negative),
        gap="medium",
    )

    for col, (_, row) in zip(
        driver_cols,
        negative.iterrows(),
    ):

        signals = []

        if row["return_rate_change"] >= 2:

            signals.append(
                f"Returns ↑{row['return_rate_change']:.2f} pp"
            )

        if row["margin_change"] <= -0.5:

            signals.append(
                f"Margin ↓{abs(row['margin_change']):.2f} pp"
            )

        if row["discount_rate_change"] >= 0.3:

            signals.append(
                f"Discount ↑{row['discount_rate_change']:.2f} pp"
            )

        if row["revenue_change_percent"] < -3:

            signals.append(
                f"Revenue ↓{abs(row['revenue_change_percent']):.2f}%"
            )

        signal_html = "".join(
            f'<span class="driver-signal">{signal}</span>'
            for signal in signals[:3]
        )

        with col:

            st.html(
                f"""
                <div class="driver-card">

                    <div class="driver-name">
                        {row["category"]}
                    </div>

                    <div class="driver-impact-label">
                        Profit Impact
                    </div>

                    <div class="driver-impact">
                        {format_rupees(abs(row["profit_change"]))}
                    </div>

                    <div style="
                        color:#dc2626;
                        font-size:0.78rem;
                        font-weight:750;
                        margin-top:0.15rem;
                    ">
                        {row["profit_change_percent"]:.2f}%
                    </div>

                    <div style="
                        margin-top:0.45rem;
                    ">
                        {signal_html}
                    </div>

                </div>
                """
            )


# ============================================================
# 8. MANAGEMENT ACTION PLAN
# ============================================================

section_title(
    "Management Action Plan",
    "Priority actions derived from the identified business drivers.",
)


def recommendation_for(row):

    category = row["category"]

    if row["return_rate_change"] >= 2:

        return (
            (
                f"Review the top-returning "
                f"{category} SKUs and return reasons. "
                f"Prioritize product quality, listing "
                f"accuracy and fulfillment issues before "
                f"expanding promotions."
            ),
            (
                "Reduce refund leakage and "
                "restore category profitability."
            ),
        )

    if (
        row["discount_rate_change"] >= 0.3
        and row["margin_change"] < 0
    ):

        return (
            (
                f"Review {category} promotional "
                f"products and discount depth. "
                f"Reduce discounts where incremental "
                f"volume does not compensate for "
                f"lost margin."
            ),
            (
                "Protect contribution margin."
            ),
        )

    if row["margin_change"] < 0:

        return (
            (
                f"Review {category} product-level "
                f"pricing, cost and discount pressure "
                f"to identify the largest sources "
                f"of margin erosion."
            ),
            (
                "Restore category margin while "
                "protecting profitable demand."
            ),
        )

    return (
        (
            f"Review the largest profit-declining "
            f"products within {category} before "
            f"changing growth investment."
        ),
        (
            "Identify the specific driver "
            "of profit deterioration."
        ),
    )


if not negative.empty:

    action_cols = st.columns(
        len(negative),
        gap="medium",
    )

    for index, (
        col,
        (_, row),
    ) in enumerate(
        zip(
            action_cols,
            negative.iterrows(),
        ),
        start=1,
    ):

        solution, objective = recommendation_for(row)

        with col:

            st.html(
                f"""
                <div class="action-card">

                    <div class="action-number">
                        ACTION {index:02d}
                    </div>

                    <div class="action-category">
                        {row["category"]}
                    </div>

                    <span class="priority-high">
                        HIGH PRIORITY
                    </span>

                    <div class="action-label">
                        Problem
                    </div>

                    <div class="action-text">
                        Profit declined
                        <strong>
                            {abs(row["profit_change_percent"]):.2f}%
                        </strong>
                        with identified impact of
                        <strong>
                            {format_rupees(abs(row["profit_change"]))}
                        </strong>.
                    </div>

                    <div class="action-label">
                        Recommended Action
                    </div>

                    <div class="action-text">
                        {solution}
                    </div>

                    <div class="action-label">
                        Objective
                    </div>

                    <div class="action-text">
                        {objective}
                    </div>

                </div>
                """
            )


# ============================================================
# 9. MARKETING DATA
# ============================================================

marketing_query = """
SELECT
    channel,
    SUM(spend) AS spend,
    SUM(revenue_generated)
        AS revenue_generated,
    SUM(new_customers)
        AS new_customers,
    SUM(conversions)
        AS conversions,
    SUM(impressions)
        AS impressions,
    SUM(clicks)
        AS clicks
FROM marketing_campaigns
WHERE campaign_date >= :start_date
  AND campaign_date <= :end_date
GROUP BY channel
ORDER BY spend DESC
"""


try:

    marketing_df = read_sql(
        marketing_query,
        {
            "start_date": start_date,
            "end_date": end_date,
        },
    )

except Exception:

    marketing_df = pd.DataFrame()


if not marketing_df.empty:

    marketing_df["roas"] = (
        marketing_df["revenue_generated"]
        /
        marketing_df["spend"]
        .replace(0, pd.NA)
    ).fillna(0)

    marketing_df["cac"] = (
        marketing_df["spend"]
        /
        marketing_df["new_customers"]
        .replace(0, pd.NA)
    ).fillna(0)

    marketing_df["conversion_rate"] = (
        marketing_df["conversions"]
        /
        marketing_df["clicks"]
        .replace(0, pd.NA)
        * 100
    ).fillna(0)


# ============================================================
# 10. GROWTH + RISK
# ============================================================

section_title("Growth Opportunity")

growth_col, risk_col = st.columns(
    [1.15, 1],
    gap="medium",
)


with growth_col:

    if not growing.empty:

        opportunity = growing.iloc[0]

        return_change = safe_float(
            opportunity["return_rate_change"]
        )

        st.html(
            f"""
            <div class="growth-card">

                <span class="growth-badge">
                    Strongest Positive Category
                </span>

                <div class="growth-title">
                    {opportunity["category"]}
                </div>

                <div style="
                    display:flex;
                    gap:2.5rem;
                    margin-top:1.25rem;
                ">

                    <div>
                        <div class="growth-stat-label">
                            Revenue
                        </div>

                        <div class="growth-stat">
                            {opportunity["revenue_change_percent"]:+.2f}%
                        </div>
                    </div>

                    <div>
                        <div class="growth-stat-label">
                            Profit
                        </div>

                        <div class="growth-stat">
                            {opportunity["profit_change_percent"]:+.2f}%
                        </div>
                    </div>

                    <div>
                        <div class="growth-stat-label">
                            Return Rate
                        </div>

                        <div class="growth-stat">
                            {return_change:+.2f} pp
                        </div>
                    </div>

                </div>

                <div style="
                    color:#6b7280;
                    font-size:0.78rem;
                    line-height:1.5;
                    margin-top:1.1rem;
                ">
                    Management consideration:
                    evaluate controlled expansion while
                    monitoring margin and return performance.
                </div>

            </div>
            """
        )

    else:

        st.html(
            """
            <div class="growth-card">

                <span class="growth-badge">
                    Growth Opportunity
                </span>

                <div class="growth-title">
                    No significant positive category
                    movement identified
                </div>

                <div style="
                    color:#6b7280;
                    font-size:0.8rem;
                    margin-top:0.75rem;
                ">
                    Continue monitoring category-level
                    profitability before increasing growth
                    investment.
                </div>

            </div>
            """
        )


# ============================================================
# RISK RADAR
# ============================================================

risk_items = []


if not marketing_df.empty:

    lowest_roas = (
        marketing_df
        .sort_values("roas")
        .iloc[0]
    )

    highest_spend = (
        marketing_df
        .sort_values(
            "spend",
            ascending=False,
        )
        .iloc[0]
    )

    if (
        lowest_roas["channel"]
        ==
        highest_spend["channel"]
    ):

        risk_items.append(
            {
                "severity": "ATTENTION",
                "title": (
                    f"{lowest_roas['channel']} efficiency"
                ),
                "detail": (
                    f"Spend "
                    f"{format_rupees(highest_spend['spend'])} "
                    f"with ROAS "
                    f"{lowest_roas['roas']:.2f}x."
                ),
                "action": (
                    "Review campaign-level efficiency "
                    "before increasing spend."
                ),
            }
        )


try:

    inventory_query = """
    WITH latest AS (

        SELECT DISTINCT ON (product_id)

            product_id,
            closing_stock,
            reorder_level,
            units_sold,
            date

        FROM inventory

        WHERE date <= :end_date

        ORDER BY
            product_id,
            date DESC
    )

    SELECT

        COUNT(*) AS risk_products,

        COALESCE(
            SUM(units_sold),
            0
        ) AS units_sold

    FROM latest

    WHERE closing_stock <= reorder_level
    """

    inventory_risk = read_sql(
        inventory_query,
        {
            "end_date": end_date,
        },
    ).iloc[0]

    risk_products = int(
        inventory_risk["risk_products"]
    )

    if risk_products >= 10:

        risk_items.append(
            {
                "severity": "WATCH",
                "title": "Inventory pressure",
                "detail": (
                    f"{risk_products} products "
                    f"are at or below reorder level."
                ),
                "action": (
                    "Prioritize high-demand SKUs "
                    "for replenishment."
                ),
            }
        )

except Exception:
    pass


with risk_col:

    st.html(
        """
        <div class="section-label"
             style="margin-top:0;">
            Risk Radar
        </div>
        """
    )

    if risk_items:

        for item in risk_items[:3]:

            severity_class = (
                "risk-attention"
                if item["severity"] == "ATTENTION"
                else "risk-watch"
            )

            st.html(
                f"""
                <div class="risk-card {severity_class}">

                    <div class="risk-severity">
                        {item["severity"]}
                    </div>

                    <div class="risk-title">
                        {item["title"]}
                    </div>

                    <div class="risk-detail">
                        {item["detail"]}
                    </div>

                    <div class="risk-action">
                        {item["action"]}
                    </div>

                </div>
                """
            )

    else:

        st.html(
            """
            <div class="risk-card risk-watch">

                <div class="risk-severity">
                    NORMAL
                </div>

                <div class="risk-title">
                    No major risk signal detected
                </div>

                <div class="risk-detail">
                    No configured risk threshold was
                    breached for the selected period.
                </div>

            </div>
            """
        )


# ============================================================
# 11. BUSINESS TRENDS
# ============================================================

section_title(
    "Business Trends",
    "Revenue and profit movement over the previous 12 months.",
)


trend_query = """
SELECT
    DATE_TRUNC(
        'month',
        o.order_date
    ) AS month,

    SUM(
        oi.revenue
    ) AS revenue,

    SUM(
        oi.profit
    ) AS profit

FROM orders o

JOIN order_items oi
    ON o.order_id = oi.order_id

WHERE o.order_status = 'Delivered'

  AND o.order_date >= (
      :start_date
      - INTERVAL '11 months'
  )

  AND o.order_date < (
      :end_date
      + INTERVAL '1 day'
  )

GROUP BY 1

ORDER BY 1
"""


try:

    trend_df = read_sql(
        trend_query,
        {
            "start_date": start_date,
            "end_date": end_date,
        },
    )

except Exception:

    trend_df = pd.DataFrame()


if not trend_df.empty:

    trend_df["month"] = pd.to_datetime(
        trend_df["month"]
    )

    trend_df["revenue"] = pd.to_numeric(
        trend_df["revenue"],
        errors="coerce",
    ).fillna(0)

    trend_df["profit"] = pd.to_numeric(
        trend_df["profit"],
        errors="coerce",
    ).fillna(0)

    trend_col1, trend_col2 = st.columns(
        2,
        gap="medium",
    )

    with trend_col1:

        revenue_fig = go.Figure()

        revenue_fig.add_trace(
            go.Scatter(
                x=trend_df["month"],
                y=trend_df["revenue"],
                mode="lines+markers",
                name="Revenue",
                line=dict(width=3),
                marker=dict(size=6),
                hovertemplate=(
                    "%{x|%b %Y}"
                    "<br>Revenue: ₹%{y:,.0f}"
                    "<extra></extra>"
                ),
            )
        )

        revenue_fig.update_layout(
            title="Revenue Trend",
            height=330,
            margin=dict(
                l=15,
                r=15,
                t=50,
                b=15,
            ),
            template="plotly_white",
            showlegend=False,
            hovermode="x",
            xaxis_title=None,
            yaxis_title=None,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

        st.plotly_chart(
            revenue_fig,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "responsive": True,
            },
        )

    with trend_col2:

        profit_fig = go.Figure()

        profit_fig.add_trace(
            go.Scatter(
                x=trend_df["month"],
                y=trend_df["profit"],
                mode="lines+markers",
                name="Profit",
                line=dict(width=3),
                marker=dict(size=6),
                hovertemplate=(
                    "%{x|%b %Y}"
                    "<br>Profit: ₹%{y:,.0f}"
                    "<extra></extra>"
                ),
            )
        )

        profit_fig.update_layout(
            title="Profit Trend",
            height=330,
            margin=dict(
                l=15,
                r=15,
                t=50,
                b=15,
            ),
            template="plotly_white",
            showlegend=False,
            hovermode="x",
            xaxis_title=None,
            yaxis_title=None,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

        st.plotly_chart(
            profit_fig,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "responsive": True,
            },
        )


# ============================================================
# 12. MARKETING SNAPSHOT
# ============================================================

if not marketing_df.empty:

    section_title(
        "Marketing Snapshot",
        "Marketing efficiency for the selected period.",
    )

    marketing_sorted = marketing_df.sort_values(
        "roas",
        ascending=False,
    )

    marketing_cols = st.columns(4)

    top_roas = marketing_sorted.iloc[0]

    lowest_roas = marketing_sorted.iloc[-1]

    total_spend = marketing_df["spend"].sum()

    total_marketing_revenue = (
        marketing_df["revenue_generated"].sum()
    )

    overall_roas = (
        total_marketing_revenue / total_spend
        if total_spend
        else 0
    )

    with marketing_cols[0]:

        st.metric(
            "Overall ROAS",
            f"{overall_roas:.2f}x",
        )

    with marketing_cols[1]:

        st.metric(
            "Highest ROAS",
            f"{top_roas['roas']:.2f}x",
            top_roas["channel"],
        )

    with marketing_cols[2]:

        st.metric(
            "Lowest ROAS",
            f"{lowest_roas['roas']:.2f}x",
            lowest_roas["channel"],
        )

    with marketing_cols[3]:

        st.metric(
            "Marketing Spend",
            format_rupees(total_spend),
        )


# ============================================================
# 13. ASK AI
# ============================================================

st.markdown("---")

st.html(
    """
    <div class="ai-card">

        <div class="ai-title">
            🤖 Ask AI
        </div>

        <div class="ai-description">
            Ask a natural-language business question
            and let the agent investigate the selected
            business period.
        </div>

    </div>
    """
)


with st.container(border=True):

    question = st.text_input(
        "Business question",
        placeholder=(
            "Why did profit decrease in September?"
        ),
        key="ceo_question",
    )

    analyze_button = st.button(
        "Analyze Business Question",
        type="primary",
        key="ask_ai_button",
    )


    if analyze_button:

        if not question.strip():

            st.warning(
                "Please enter a business question."
            )

        else:

            payload = {
                "question": question,
                "start_date": str(start_date),
                "end_date": str(end_date),
            }

            try:

                with st.spinner(
                    "Analyzing business data..."
                ):

                    response = requests.post(
                        (
                            f"{API_BASE_URL}"
                            "/api/agent/ask"
                        ),
                        json=payload,
                        timeout=60,
                    )

                response.raise_for_status()

                result = response.json()

                intent = (
                    result.get("intent")
                    or {}
                )

                metric = intent.get(
                    "metric"
                )

                # ------------------------------------------------
                # MARKETING RESPONSE
                # ------------------------------------------------

                marketing = (
                    result.get("marketing")
                    or {}
                )

                marketing_analysis = (
                    marketing.get("analysis")
                    or {}
                )

                marketing_recommendations = (
                    marketing.get("recommendations")
                    or []
                )

                if (
                    metric in {
                        "roas",
                        "cac",
                        "conversion_rate",
                    }
                    or
                    "marketing"
                    in intent.get(
                        "type",
                        "",
                    )
                ):

                    st.markdown(
                        "### Marketing Analysis"
                    )

                    marketing_channels = (
                        marketing_analysis.get(
                            "channels"
                        )
                        or []
                    )

                    requested_channel = None

                    question_lower = (
                        question.lower()
                    )

                    for channel in marketing_channels:

                        channel_name = str(
                            channel.get(
                                "channel",
                                "",
                            )
                        )

                        if (
                            channel_name.lower()
                            in question_lower
                        ):

                            requested_channel = (
                                channel
                            )

                            break

                    if requested_channel:

                        channel_name = (
                            requested_channel.get(
                                "channel",
                                "Unknown",
                            )
                        )

                        roas = safe_float(
                            requested_channel.get(
                                "roas"
                            )
                        )

                        spend = safe_float(
                            requested_channel.get(
                                "spend"
                            )
                        )

                        revenue_generated = (
                            safe_float(
                                requested_channel.get(
                                    "revenue_generated"
                                )
                            )
                        )

                        conversions = int(
                            safe_float(
                                requested_channel.get(
                                    "conversions"
                                )
                            )
                        )

                        new_customers = int(
                            safe_float(
                                requested_channel.get(
                                    "new_customers"
                                )
                            )
                        )

                        cac = safe_float(
                            requested_channel.get(
                                "customer_acquisition_cost",
                                requested_channel.get(
                                    "cac",
                                    0,
                                ),
                            )
                        )

                        conversion_rate = safe_float(
                            requested_channel.get(
                                "conversion_rate"
                            )
                        )

                        st.markdown(
                            f"#### {channel_name}"
                        )

                        m1, m2, m3 = st.columns(3)

                        with m1:

                            st.metric(
                                "ROAS",
                                f"{roas:.2f}x",
                            )

                        with m2:

                            st.metric(
                                "Spend",
                                format_rupees(
                                    spend
                                ),
                            )

                        with m3:

                            st.metric(
                                "Revenue Generated",
                                format_rupees(
                                    revenue_generated
                                ),
                            )

                        m4, m5, m6 = st.columns(3)

                        with m4:

                            st.metric(
                                "Conversions",
                                f"{conversions:,}",
                            )

                        with m5:

                            st.metric(
                                "New Customers",
                                f"{new_customers:,}",
                            )

                        with m6:

                            st.metric(
                                "CAC",
                                format_rupees(
                                    cac
                                ),
                            )

                        total_spend = sum(
                            safe_float(
                                item.get("spend")
                            )
                            for item
                            in marketing_channels
                        )

                        total_revenue = sum(
                            safe_float(
                                item.get(
                                    "revenue_generated"
                                )
                            )
                            for item
                            in marketing_channels
                        )

                        overall_roas = (
                            total_revenue
                            / total_spend
                            if total_spend
                            else 0
                        )

                        if (
                            overall_roas
                            and roas < overall_roas
                        ):

                            st.warning(
                                f"{channel_name} generated "
                                f"{roas:.2f}x ROAS, below "
                                f"overall marketing ROAS "
                                f"of {overall_roas:.2f}x."
                            )

                        else:

                            st.info(
                                f"{channel_name} generated "
                                f"{roas:.2f}x ROAS."
                            )

                        st.caption(
                            "Marketing efficiency is an "
                            "evidence signal. It does not by "
                            "itself establish that the channel "
                            "caused a change in business profit."
                        )

                    else:

                        top_roas = (
                            marketing_analysis.get(
                                "top_roas_channel"
                            )
                        )

                        lowest_roas_result = (
                            marketing_analysis.get(
                                "lowest_roas_channel"
                            )
                        )

                        if top_roas:

                            st.write(
                                f"Highest ROAS: "
                                f"**{top_roas.get('channel')}** "
                                f"at "
                                f"**{safe_float(top_roas.get('roas')):.2f}x**."
                            )

                        if lowest_roas_result:

                            st.write(
                                f"Lowest ROAS: "
                                f"**{lowest_roas_result.get('channel')}** "
                                f"at "
                                f"**{safe_float(lowest_roas_result.get('roas')):.2f}x**."
                            )

                    if marketing_recommendations:

                        st.markdown(
                            "### Recommended Actions"
                        )

                        for recommendation in (
                            marketing_recommendations[:5]
                        ):

                            st.write(
                                "•",
                                recommendation.get(
                                    "action",
                                    "",
                                ),
                            )

                            reason = (
                                recommendation.get(
                                    "reason"
                                )
                            )

                            if reason:

                                st.caption(
                                    reason
                                )

                # ------------------------------------------------
                # STANDARD BUSINESS RESPONSE
                # ------------------------------------------------

                else:

                    analysis = (
                        result.get("analysis")
                        or {}
                    )

                    if analysis:

                        current_value = safe_float(
                            analysis.get(
                                "current_value",
                                0,
                            )
                        )

                        change = safe_float(
                            analysis.get(
                                "change_percent",
                                0,
                            )
                        )

                        st.markdown(
                            "### Business Result"
                        )

                        result_col1, result_col2 = (
                            st.columns(2)
                        )

                        with result_col1:

                            st.metric(
                                "Current Result",
                                format_metric_value(
                                    metric,
                                    current_value,
                                ),
                                f"{change:+.2f}%",
                            )

                        with result_col2:

                            st.metric(
                                "Metric",
                                str(
                                    metric or "business"
                                ).replace(
                                    "_",
                                    " ",
                                ).title(),
                            )

                    root_cause = (
                        result.get(
                            "root_cause"
                        )
                    )

                    if root_cause:

                        largest = (
                            root_cause.get(
                                "largest_profit_decline"
                            )
                        )

                        if largest:

                            st.markdown(
                                "### Root Cause"
                            )

                            st.write(
                                (
                                    f"**{largest.get('category', 'Unknown')}** "
                                    f"profit changed "
                                    f"{safe_float(largest.get('profit_change_percent')):.2f}%."
                                )
                            )

                        return_pressure = (
                            root_cause.get(
                                "highest_return_pressure"
                            )
                        )

                        if return_pressure:

                            return_change = safe_float(
                                return_pressure.get(
                                    "return_rate_change_percentage_points",
                                    return_pressure.get(
                                        "return_rate_change",
                                        0,
                                    ),
                                )
                            )

                            st.write(
                                (
                                    f"Return pressure: "
                                    f"**{return_pressure.get('category', 'Unknown')}** "
                                    f"({return_change:+.2f} pp)."
                                )
                            )

                    recommendations = (
                        result.get(
                            "recommendations",
                            [],
                        )
                    )

                    if recommendations:

                        st.markdown(
                            "### Recommended Actions"
                        )

                        for recommendation in (
                            recommendations[:5]
                        ):

                            st.write(
                                "•",
                                recommendation.get(
                                    "action",
                                    "",
                                ),
                            )

                            reason = (
                                recommendation.get(
                                    "reason"
                                )
                            )

                            if reason:

                                st.caption(
                                    reason
                                )

            except requests.exceptions.ConnectionError:

                st.error(
                    "FastAPI is not reachable. "
                    "Start the backend first."
                )

            except requests.exceptions.Timeout:

                st.error(
                    "AI analysis timed out."
                )

            except requests.exceptions.HTTPError as exc:

                st.error(
                    f"Agent API error: {exc}"
                )

            except Exception as exc:

                st.error(
                    f"AI analysis failed: {exc}"
                )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.html(
    """
    <div style="
        text-align:center;
        color:#9ca3af;
        font-size:0.7rem;
        padding:0.5rem;
    ">
        E-Commerce Agentic BI
        &nbsp;·&nbsp;
        Executive Decision Support
        &nbsp;·&nbsp;
        SEE → UNDERSTAND → ACT
    </div>
    """
)