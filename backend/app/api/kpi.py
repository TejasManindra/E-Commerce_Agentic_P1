from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import date

from app.database.database import get_db

router = APIRouter(prefix="/api/kpi", tags=["KPI"])


@router.get("/overview")
def get_overview(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):

    query = text("""
        WITH current_period AS (
            SELECT
                COALESCE(SUM(o.total_amount), 0) AS revenue,
                COUNT(DISTINCT o.order_id) AS orders,
                COUNT(DISTINCT o.customer_id) AS customers
            FROM orders o
            WHERE o.order_status = 'Delivered'
              AND o.order_date >= :start_date
              AND o.order_date < :end_date + INTERVAL '1 day'
        ),

        profit_data AS (
            SELECT
                COALESCE(SUM(oi.profit), 0) AS profit
            FROM order_items oi
            JOIN orders o
                ON oi.order_id = o.order_id
            WHERE o.order_status = 'Delivered'
              AND o.order_date >= :start_date
              AND o.order_date < :end_date + INTERVAL '1 day'
        ),

        target_data AS (
            SELECT
                COALESCE(SUM(revenue_target), 0) AS revenue_target
            FROM targets
            WHERE month >= TO_CHAR(:start_date, 'YYYY-MM')
              AND month <= TO_CHAR(:end_date, 'YYYY-MM')
        )

        SELECT
            cp.revenue,
            cp.orders,
            cp.customers,
            pd.profit,
            td.revenue_target
        FROM current_period cp
        CROSS JOIN profit_data pd
        CROSS JOIN target_data td;
    """)

    result = db.execute(
        query,
        {
            "start_date": start_date,
            "end_date": end_date
        }
    ).mappings().one()

    revenue = float(result["revenue"])
    orders = int(result["orders"])
    customers = int(result["customers"])
    profit = float(result["profit"])
    revenue_target = float(result["revenue_target"])

    aov = revenue / orders if orders else 0
    profit_margin = (profit / revenue * 100) if revenue else 0
    target_achievement = (
        revenue / revenue_target * 100
        if revenue_target
        else 0
    )

    return {
        "period": {
            "start_date": str(start_date),
            "end_date": str(end_date)
        },
        "revenue": round(revenue, 2),
        "orders": orders,
        "customers": customers,
        "aov": round(aov, 2),
        "profit": round(profit, 2),
        "profit_margin_percent": round(profit_margin, 2),
        "revenue_target": round(revenue_target, 2),
        "target_achievement_percent": round(target_achievement, 2)
    }