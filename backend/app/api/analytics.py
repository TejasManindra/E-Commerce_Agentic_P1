from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.database import get_db

router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"]
)


@router.get("/revenue-profit-trend")
def get_revenue_profit_trend(
    db: Session = Depends(get_db)
):
    query = text("""
        WITH revenue_by_month AS (
            SELECT
                DATE_TRUNC('month', order_date) AS month_date,
                COALESCE(SUM(total_amount), 0) AS revenue
            FROM orders
            WHERE order_status = 'Delivered'
            GROUP BY DATE_TRUNC('month', order_date)
        ),

        profit_by_month AS (
            SELECT
                DATE_TRUNC('month', o.order_date) AS month_date,
                COALESCE(SUM(oi.profit), 0) AS profit
            FROM orders o
            JOIN order_items oi
                ON o.order_id = oi.order_id
            WHERE o.order_status = 'Delivered'
            GROUP BY DATE_TRUNC('month', o.order_date)
        )

        SELECT
            TO_CHAR(r.month_date, 'YYYY-MM') AS month,
            ROUND(r.revenue::numeric, 2) AS revenue,
            ROUND(COALESCE(p.profit, 0)::numeric, 2) AS profit
        FROM revenue_by_month r
        LEFT JOIN profit_by_month p
            ON r.month_date = p.month_date
        ORDER BY r.month_date;
    """)

    results = db.execute(query).mappings().all()

    return {
        "data": [
            {
                "month": row["month"],
                "revenue": float(row["revenue"]),
                "profit": float(row["profit"])
            }
            for row in results
        ]
    }