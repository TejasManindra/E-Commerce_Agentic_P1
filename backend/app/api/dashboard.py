from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.database import get_db


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Executive Dashboard"]
)


@router.get("/executive-summary")
def get_executive_summary(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    # ============================================================
    # Validate date range
    # ============================================================

    if end_date < start_date:
        return {
            "error": "end_date must be greater than or equal to start_date"
        }

    # Number of days in selected period
    period_days = (end_date - start_date).days + 1

    # ============================================================
    # CURRENT PERIOD
    # ============================================================

    current_query = text("""
        SELECT

            COALESCE(SUM(oi.revenue), 0) AS revenue,

            COALESCE(SUM(oi.profit), 0) AS profit,

            COALESCE(
                SUM(
                    oi.unit_price
                    * oi.quantity
                    * oi.discount_percent
                    / 100
                ),
                0
            ) AS discounts,

            COUNT(DISTINCT o.order_id) AS orders,

            COUNT(DISTINCT o.customer_id) AS customers,

            COALESCE(
                SUM(oi.quantity),
                0
            ) AS units_sold

        FROM orders o

        JOIN order_items oi
            ON o.order_id = oi.order_id

        WHERE o.order_status = 'Delivered'

          AND o.order_date >= :start_date

          AND o.order_date < :end_date + INTERVAL '1 day'
    """)

    current = db.execute(
        current_query,
        {
            "start_date": start_date,
            "end_date": end_date
        }
    ).mappings().first()

    # ============================================================
    # PREVIOUS PERIOD
    # ============================================================

    previous_end = start_date - timedelta(days=1)

    previous_start = (
        previous_end
        - timedelta(days=period_days - 1)
    )

    previous_query = text("""
        SELECT

            COALESCE(SUM(oi.revenue), 0) AS revenue,

            COALESCE(SUM(oi.profit), 0) AS profit,

            COALESCE(
                SUM(
                    oi.unit_price
                    * oi.quantity
                    * oi.discount_percent
                    / 100
                ),
                0
            ) AS discounts,

            COUNT(DISTINCT o.order_id) AS orders,

            COUNT(DISTINCT o.customer_id) AS customers,

            COALESCE(
                SUM(oi.quantity),
                0
            ) AS units_sold

        FROM orders o

        JOIN order_items oi
            ON o.order_id = oi.order_id

        WHERE o.order_status = 'Delivered'

          AND o.order_date >= :start_date

          AND o.order_date < :end_date + INTERVAL '1 day'
    """)

    previous = db.execute(
        previous_query,
        {
            "start_date": previous_start,
            "end_date": previous_end
        }
    ).mappings().first()

    # ============================================================
    # CURRENT VALUES
    # ============================================================

    revenue = float(current["revenue"])
    profit = float(current["profit"])
    discounts = float(current["discounts"])

    orders = int(current["orders"])
    customers = int(current["customers"])
    units_sold = int(current["units_sold"])

    # ============================================================
    # PREVIOUS VALUES
    # ============================================================

    previous_revenue = float(previous["revenue"])
    previous_profit = float(previous["profit"])
    previous_discounts = float(previous["discounts"])

    previous_orders = int(previous["orders"])
    previous_customers = int(previous["customers"])
    previous_units_sold = int(previous["units_sold"])

    # ============================================================
    # PROFIT MARGIN
    # ============================================================

    if revenue > 0:
        profit_margin = (
            profit / revenue
        ) * 100
    else:
        profit_margin = 0

    # ============================================================
    # PREVIOUS PROFIT MARGIN
    # ============================================================

    if previous_revenue > 0:
        previous_profit_margin = (
            previous_profit / previous_revenue
        ) * 100
    else:
        previous_profit_margin = 0

    # ============================================================
    # AVERAGE ORDER VALUE
    # ============================================================

    if orders > 0:
        average_order_value = (
            revenue / orders
        )
    else:
        average_order_value = 0

    # ============================================================
    # PREVIOUS AOV
    # ============================================================

    if previous_orders > 0:
        previous_average_order_value = (
            previous_revenue / previous_orders
        )
    else:
        previous_average_order_value = 0

    # ============================================================
    # DISCOUNT RATE
    # ============================================================

    if revenue > 0:
        discount_rate = (
            discounts / revenue
        ) * 100
    else:
        discount_rate = 0

    # ============================================================
    # PREVIOUS DISCOUNT RATE
    # ============================================================

    if previous_revenue > 0:
        previous_discount_rate = (
            previous_discounts / previous_revenue
        ) * 100
    else:
        previous_discount_rate = 0

    # ============================================================
    # GROWTH FUNCTION
    # ============================================================

    def calculate_growth(
        current_value,
        previous_value
    ):
        if previous_value == 0:
            return 0

        return (
            (current_value - previous_value)
            / previous_value
        ) * 100

    # ============================================================
    # GROWTH METRICS
    # ============================================================

    revenue_growth = calculate_growth(
        revenue,
        previous_revenue
    )

    profit_growth = calculate_growth(
        profit,
        previous_profit
    )

    orders_growth = calculate_growth(
        orders,
        previous_orders
    )

    customer_growth = calculate_growth(
        customers,
        previous_customers
    )

    units_growth = calculate_growth(
        units_sold,
        previous_units_sold
    )

    aov_growth = calculate_growth(
        average_order_value,
        previous_average_order_value
    )

    discount_growth = calculate_growth(
        discounts,
        previous_discounts
    )

    # ============================================================
    # PROFIT MARGIN CHANGE
    # ============================================================

    margin_change = (
        profit_margin
        - previous_profit_margin
    )

    # ============================================================
    # BUSINESS HEALTH STATUS
    # ============================================================

    if profit < 0:

        business_status = "Critical"

    elif profit_margin < 10:

        business_status = "Needs Attention"

    elif profit_growth < 0 and revenue_growth > 0:

        business_status = "Needs Attention"

    else:

        business_status = "Healthy"

    # ============================================================
    # RETURN EXECUTIVE SUMMARY
    # ============================================================

    return {

        "period": {
            "start_date": str(start_date),
            "end_date": str(end_date),
            "days": period_days
        },

        "previous_period": {
            "start_date": str(previous_start),
            "end_date": str(previous_end),
            "days": period_days
        },

        "business_status": business_status,

        "kpis": {

            "revenue": round(
                revenue,
                2
            ),

            "revenue_growth_percent": round(
                revenue_growth,
                2
            ),

            "orders": orders,

            "orders_growth_percent": round(
                orders_growth,
                2
            ),

            "profit": round(
                profit,
                2
            ),

            "profit_growth_percent": round(
                profit_growth,
                2
            ),

            "profit_margin_percent": round(
                profit_margin,
                2
            ),

            "profit_margin_change_percent": round(
                margin_change,
                2
            ),

            "customers": customers,

            "customer_growth_percent": round(
                customer_growth,
                2
            ),

            "average_order_value": round(
                average_order_value,
                2
            ),

            "aov_growth_percent": round(
                aov_growth,
                2
            ),

            "discounts": round(
                discounts,
                2
            ),

            "discount_rate_percent": round(
                discount_rate,
                2
            ),

            "discount_growth_percent": round(
                discount_growth,
                2
            ),

            "units_sold": units_sold,

            "units_growth_percent": round(
                units_growth,
                2
            )
        }
    }