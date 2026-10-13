from datetime import date, timedelta

from app.agents.query_understanding_agent import QueryIntent


# ============================================================
# METRIC SQL DEFINITIONS
# ============================================================

METRIC_SQL = {

    "revenue":
        "SUM(oi.revenue)",

    "profit":
        "SUM(oi.profit)",

    "orders":
        "COUNT(DISTINCT o.order_id)",

    "customers":
        "COUNT(DISTINCT o.customer_id)",

    "units_sold":
        "SUM(oi.quantity)",

    "discounts":
        """
        SUM(
            oi.unit_price
            * oi.quantity
            * oi.discount_percent
            / 100
        )
        """,
}


# ============================================================
# DIMENSION SQL
# ============================================================

DIMENSION_SQL = {

    "category":
        "p.category",

    "product":
        "p.product_name",

    "state":
        "o.shipping_state",

    "channel":
        "o.channel",

    "month":
        "DATE_TRUNC('month', o.order_date)",

}


# ============================================================
# MONTH ARITHMETIC
# ============================================================

def _subtract_months(
    year: int,
    month: int,
    count: int,
):

    total_months = (
        year * 12
        + (month - 1)
        - count
    )

    new_year = (
        total_months // 12
    )

    new_month = (
        total_months % 12
    ) + 1

    return new_year, new_month


def _first_day_previous_months(
    reference_date: date,
    months_back: int,
) -> date:

    year, month = (
        _subtract_months(
            reference_date.year,
            reference_date.month,
            months_back,
        )
    )

    return date(
        year,
        month,
        1,
    )


# ============================================================
# GENERAL BUSINESS QUERY → SQL
# ============================================================

def generate_sql(
    intent: QueryIntent,
):

    if (
        not intent.start_date
        or not intent.end_date
    ):

        raise ValueError(
            "Start date and end date are required."
        )

    metric_sql = METRIC_SQL.get(
        intent.metric
    )

    if not metric_sql:

        raise ValueError(
            f"Unsupported metric: {intent.metric}"
        )

    start_date = intent.start_date

    end_date = intent.end_date

    # ========================================================
    # MULTI-PERIOD MONTHLY COMPARISON
    # ========================================================

    if (
        intent.comparison
        == "previous_periods"
    ):

        period_count = (
            intent.period_count or 3
        )

        # We intentionally anchor to the month
        # BEFORE the selected analysis period.
        #
        # Example:
        # selected period = September 2026
        # previous 3 months = June, July, August

        analysis_month_start = date(
            start_date.year,
            start_date.month,
            1,
        )

        query_start = (
            _first_day_previous_months(
                analysis_month_start,
                period_count,
            )
        )

        query_end = (
            analysis_month_start
        )

        sql = f"""

            SELECT

                DATE_TRUNC(
                    'month',
                    o.order_date
                ) AS period,

                {metric_sql} AS value

            FROM order_items oi

            JOIN orders o
                ON oi.order_id = o.order_id

            WHERE o.order_status = 'Delivered'

              AND o.order_date >= :period_start

              AND o.order_date < :period_end

            GROUP BY
                DATE_TRUNC(
                    'month',
                    o.order_date
                )

            ORDER BY period ASC

        """

        params = {

            "period_start":
                query_start,

            "period_end":
                query_end,

        }

        return sql, params

    # ========================================================
    # CURRENT PERIOD VS PREVIOUS PERIOD
    # ========================================================

    if (
        intent.comparison
        == "previous_period"
    ):

        days = (
            end_date - start_date
        ).days + 1

        previous_end = (
            start_date
            - timedelta(days=1)
        )

        previous_start = (
            previous_end
            - timedelta(days=days - 1)
        )

        sql = f"""

            SELECT

                'current' AS period,

                {metric_sql} AS value

            FROM order_items oi

            JOIN orders o
                ON oi.order_id = o.order_id

            WHERE o.order_status = 'Delivered'

              AND o.order_date >= :current_start

              AND o.order_date
                  < :current_end
                    + INTERVAL '1 day'

            UNION ALL

            SELECT

                'previous' AS period,

                {metric_sql} AS value

            FROM order_items oi

            JOIN orders o
                ON oi.order_id = o.order_id

            WHERE o.order_status = 'Delivered'

              AND o.order_date >= :previous_start

              AND o.order_date
                  < :previous_end
                    + INTERVAL '1 day'

        """

        params = {

            "current_start":
                start_date,

            "current_end":
                end_date,

            "previous_start":
                previous_start,

            "previous_end":
                previous_end,

        }

        return sql, params

    # ========================================================
    # DIMENSION ANALYSIS
    # ========================================================

    if intent.dimension:

        dimension_sql = (
            DIMENSION_SQL.get(
                intent.dimension
            )
        )

        if not dimension_sql:

            raise ValueError(
                f"Unsupported dimension: "
                f"{intent.dimension}"
            )

        sql = f"""

            SELECT

                {dimension_sql}
                    AS dimension,

                {metric_sql}
                    AS value,

                SUM(oi.profit)
                    AS profit

            FROM order_items oi

            JOIN orders o
                ON oi.order_id = o.order_id

            JOIN products p
                ON oi.product_id = p.product_id

            WHERE o.order_status = 'Delivered'

              AND o.order_date >= :start_date

              AND o.order_date
                  < :end_date
                    + INTERVAL '1 day'

            GROUP BY
                {dimension_sql}

            ORDER BY value DESC

        """

        params = {

            "start_date":
                start_date,

            "end_date":
                end_date,

        }

        return sql, params

    # ========================================================
    # SIMPLE KPI
    # ========================================================

    sql = f"""

        SELECT

            {metric_sql}
                AS value,

            SUM(oi.profit)
                AS profit

        FROM order_items oi

        JOIN orders o
            ON oi.order_id = o.order_id

        WHERE o.order_status = 'Delivered'

          AND o.order_date >= :start_date

          AND o.order_date
              < :end_date
                + INTERVAL '1 day'

    """

    params = {

        "start_date":
            start_date,

        "end_date":
            end_date,

    }

    return sql, params


# ============================================================
# ROOT CAUSE SQL
# ============================================================

def generate_root_cause_sql(
    start_date: date,
    end_date: date,
):

    period_days = (
        end_date - start_date
    ).days + 1

    previous_end = (
        start_date
        - timedelta(days=1)
    )

    previous_start = (
        previous_end
        - timedelta(days=period_days - 1)
    )

    sql = """

        WITH current_period AS (

            SELECT

                p.category,

                SUM(oi.revenue)
                    AS revenue,

                SUM(oi.profit)
                    AS profit,

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

        current_returns AS (

            SELECT

                p.category,

                SUM(r.refund_amount)
                    AS returns

            FROM returns r

            JOIN products p
                ON r.product_id = p.product_id

            WHERE r.return_date >= :current_start

              AND r.return_date <= :current_end

            GROUP BY p.category
        ),

        previous_period AS (

            SELECT

                p.category,

                SUM(oi.revenue)
                    AS revenue,

                SUM(oi.profit)
                    AS profit,

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

        previous_returns AS (

            SELECT

                p.category,

                SUM(r.refund_amount)
                    AS returns

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

            COALESCE(
                c.revenue,
                0
            ) AS current_revenue,

            COALESCE(
                p.revenue,
                0
            ) AS previous_revenue,

            COALESCE(
                c.profit,
                0
            ) AS current_profit,

            COALESCE(
                p.profit,
                0
            ) AS previous_profit,

            COALESCE(
                c.discounts,
                0
            ) AS current_discounts,

            COALESCE(
                p.discounts,
                0
            ) AS previous_discounts,

            COALESCE(
                cr.returns,
                0
            ) AS current_returns,

            COALESCE(
                pr.returns,
                0
            ) AS previous_returns

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
            );

    """

    params = {

        "current_start":
            start_date,

        "current_end":
            end_date,

        "previous_start":
            previous_start,

        "previous_end":
            previous_end,

    }

    return sql, params


# ============================================================
# MARKETING SQL
# ============================================================

def generate_marketing_sql(
    start_date: date,
    end_date: date,
):

    sql = """

        SELECT

            channel,

            SUM(spend)
                AS spend,

            SUM(revenue_generated)
                AS revenue_generated,

            SUM(conversions)
                AS conversions,

            SUM(new_customers)
                AS new_customers,

            SUM(impressions)
                AS impressions,

            SUM(clicks)
                AS clicks

        FROM marketing_campaigns

        WHERE campaign_date >= :start_date

          AND campaign_date <= :end_date

        GROUP BY channel

        ORDER BY revenue_generated DESC;

    """

    params = {

        "start_date":
            start_date,

        "end_date":
            end_date,

    }

    return sql, params