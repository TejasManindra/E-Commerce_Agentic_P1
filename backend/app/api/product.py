from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.agents.insight_agent import generate_product_insights


router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"]
)


# ============================================================
# PRODUCT PERFORMANCE
# ============================================================

@router.get("/product-performance")
def get_product_performance(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    query = text("""
        WITH product_data AS (
            SELECT
                p.product_id,
                p.product_name,
                p.category,
                COALESCE(SUM(oi.revenue), 0) AS revenue,
                COALESCE(SUM(oi.profit), 0) AS profit,
                COALESCE(SUM(oi.quantity), 0) AS units_sold,
                COUNT(DISTINCT o.order_id) AS orders

            FROM order_items oi

            JOIN orders o
                ON oi.order_id = o.order_id

            JOIN products p
                ON oi.product_id = p.product_id

            WHERE o.order_status = 'Delivered'
              AND o.order_date >= :start_date
              AND o.order_date < :end_date + INTERVAL '1 day'

            GROUP BY
                p.product_id,
                p.product_name,
                p.category
        ),

        total_data AS (
            SELECT
                COALESCE(SUM(revenue), 0) AS total_revenue
            FROM product_data
        )

        SELECT
            p.product_id,
            p.product_name,
            p.category,

            ROUND(
                p.revenue::numeric,
                2
            ) AS revenue,

            ROUND(
                p.profit::numeric,
                2
            ) AS profit,

            p.units_sold,
            p.orders,

            ROUND(
                CASE
                    WHEN p.revenue > 0
                    THEN (p.profit / p.revenue) * 100
                    ELSE 0
                END::numeric,
                2
            ) AS profit_margin_percent,

            ROUND(
                CASE
                    WHEN t.total_revenue > 0
                    THEN (p.revenue / t.total_revenue) * 100
                    ELSE 0
                END::numeric,
                2
            ) AS revenue_share_percent,

            CASE

                WHEN p.revenue >= (
                    SELECT PERCENTILE_CONT(0.75)
                    WITHIN GROUP (ORDER BY revenue)
                    FROM product_data
                )

                AND p.profit >= (
                    SELECT PERCENTILE_CONT(0.75)
                    WITHIN GROUP (ORDER BY profit)
                    FROM product_data
                )

                THEN 'Star Product'


                WHEN p.revenue >= (
                    SELECT PERCENTILE_CONT(0.75)
                    WITHIN GROUP (ORDER BY revenue)
                    FROM product_data
                )

                AND p.profit < (
                    SELECT PERCENTILE_CONT(0.50)
                    WITHIN GROUP (ORDER BY profit)
                    FROM product_data
                )

                THEN 'Revenue Trap'


                WHEN p.revenue < (
                    SELECT PERCENTILE_CONT(0.50)
                    WITHIN GROUP (ORDER BY revenue)
                    FROM product_data
                )

                AND p.profit >= (
                    SELECT PERCENTILE_CONT(0.75)
                    WITHIN GROUP (ORDER BY profit)
                    FROM product_data
                )

                THEN 'Growth Opportunity'


                ELSE 'Optimization Candidate'

            END AS performance_classification

        FROM product_data p

        CROSS JOIN total_data t

        ORDER BY p.revenue DESC;
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
                "product_id": row["product_id"],
                "product_name": row["product_name"],
                "category": row["category"],

                "revenue": float(row["revenue"]),
                "profit": float(row["profit"]),

                "units_sold": int(row["units_sold"]),
                "orders": int(row["orders"]),

                "profit_margin_percent": float(
                    row["profit_margin_percent"]
                ),

                "revenue_share_percent": float(
                    row["revenue_share_percent"]
                ),

                "performance_classification": row[
                    "performance_classification"
                ]
            }

            for row in results
        ]
    }


# ============================================================
# PRODUCT INSIGHTS
# ============================================================

@router.get("/product-insights")
def get_product_insights(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    query = text("""
        WITH product_data AS (
            SELECT
                p.product_id,
                p.product_name,
                p.category,
                COALESCE(SUM(oi.revenue), 0) AS revenue,
                COALESCE(SUM(oi.profit), 0) AS profit,
                COALESCE(SUM(oi.quantity), 0) AS units_sold,
                COUNT(DISTINCT o.order_id) AS orders

            FROM order_items oi

            JOIN orders o
                ON oi.order_id = o.order_id

            JOIN products p
                ON oi.product_id = p.product_id

            WHERE o.order_status = 'Delivered'
              AND o.order_date >= :start_date
              AND o.order_date < :end_date + INTERVAL '1 day'

            GROUP BY
                p.product_id,
                p.product_name,
                p.category
        ),

        total_data AS (
            SELECT
                COALESCE(SUM(revenue), 0) AS total_revenue
            FROM product_data
        ),

        thresholds AS (
            SELECT
                PERCENTILE_CONT(0.75)
                WITHIN GROUP (ORDER BY revenue)
                AS revenue_75,

                PERCENTILE_CONT(0.50)
                WITHIN GROUP (ORDER BY revenue)
                AS revenue_50,

                PERCENTILE_CONT(0.75)
                WITHIN GROUP (ORDER BY profit)
                AS profit_75,

                PERCENTILE_CONT(0.50)
                WITHIN GROUP (ORDER BY profit)
                AS profit_50

            FROM product_data
        )

        SELECT
            p.product_id,
            p.product_name,
            p.category,

            ROUND(
                p.revenue::numeric,
                2
            ) AS revenue,

            ROUND(
                p.profit::numeric,
                2
            ) AS profit,

            p.units_sold,
            p.orders,

            ROUND(
                CASE
                    WHEN p.revenue > 0
                    THEN (p.profit / p.revenue) * 100
                    ELSE 0
                END::numeric,
                2
            ) AS profit_margin_percent,

            ROUND(
                CASE
                    WHEN t.total_revenue > 0
                    THEN (p.revenue / t.total_revenue) * 100
                    ELSE 0
                END::numeric,
                2
            ) AS revenue_share_percent,

            CASE

                WHEN p.revenue >= th.revenue_75
                 AND p.profit >= th.profit_75

                THEN 'Star Product'


                WHEN p.revenue >= th.revenue_75
                 AND p.profit < th.profit_50

                THEN 'Revenue Trap'


                WHEN p.revenue < th.revenue_50
                 AND p.profit >= th.profit_75

                THEN 'Growth Opportunity'


                ELSE 'Optimization Candidate'

            END AS performance_classification

        FROM product_data p

        CROSS JOIN total_data t

        CROSS JOIN thresholds th

        ORDER BY p.revenue DESC;
    """)

    results = db.execute(
        query,
        {
            "start_date": start_date,
            "end_date": end_date
        }
    ).mappings().all()


    # --------------------------------------------------------
    # Convert database results into agent input
    # --------------------------------------------------------

    products = [
        {
            "product_id": row["product_id"],
            "product_name": row["product_name"],
            "category": row["category"],

            "revenue": float(row["revenue"]),
            "profit": float(row["profit"]),

            "units_sold": int(row["units_sold"]),
            "orders": int(row["orders"]),

            "profit_margin_percent": float(
                row["profit_margin_percent"]
            ),

            "revenue_share_percent": float(
                row["revenue_share_percent"]
            ),

            "performance_classification": row[
                "performance_classification"
            ]
        }

        for row in results
    ]


    # --------------------------------------------------------
    # Run Insight Agent
    # --------------------------------------------------------

    analysis = generate_product_insights(products)


    # --------------------------------------------------------
    # Return executive-level response
    # --------------------------------------------------------

    return {
        "period": {
            "start_date": str(start_date),
            "end_date": str(end_date)
        },

        "product_summary": {
            "total_products": len(products)
        },

        "insights": analysis["insights"],

        "recommendations": analysis["recommendations"]
    }