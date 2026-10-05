from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.database import get_db


router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"]
)


@router.get("/category-performance")
def get_category_performance(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    query = text("""
        WITH category_data AS (
            SELECT
                p.category,
                COALESCE(SUM(oi.revenue), 0) AS revenue,
                COALESCE(SUM(oi.profit), 0) AS profit,
                COUNT(DISTINCT o.order_id) AS orders
            FROM order_items oi
            JOIN orders o
                ON oi.order_id = o.order_id
            JOIN products p
                ON oi.product_id = p.product_id
            WHERE o.order_status = 'Delivered'
              AND o.order_date >= :start_date
              AND o.order_date < :end_date + INTERVAL '1 day'
            GROUP BY p.category
        ),

        total_data AS (
            SELECT
                COALESCE(SUM(revenue), 0) AS total_revenue
            FROM category_data
        )

        SELECT
            c.category,
            ROUND(c.revenue::numeric, 2) AS revenue,
            ROUND(c.profit::numeric, 2) AS profit,
            c.orders,

            ROUND(
                CASE
                    WHEN c.revenue > 0
                    THEN (c.profit / c.revenue) * 100
                    ELSE 0
                END::numeric,
                2
            ) AS profit_margin_percent,

            ROUND(
                CASE
                    WHEN t.total_revenue > 0
                    THEN (c.revenue / t.total_revenue) * 100
                    ELSE 0
                END::numeric,
                2
            ) AS revenue_share_percent

        FROM category_data c
        CROSS JOIN total_data t
        ORDER BY c.revenue DESC;
    """)

    results = db.execute(
        query,
        {
            "start_date": start_date,
            "end_date": end_date
        }
    ).mappings().all()

    return {
        "period": {
            "start_date": str(start_date),
            "end_date": str(end_date)
        },
        "data": [
            {
                "category": row["category"],
                "revenue": float(row["revenue"]),
                "profit": float(row["profit"]),
                "orders": int(row["orders"]),
                "profit_margin_percent": float(row["profit_margin_percent"]),
                "revenue_share_percent": float(row["revenue_share_percent"])
            }
            for row in results
        ]
    }