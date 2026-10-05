from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.agents.root_cause_agent import analyze_root_cause
from app.agents.recommendation_agent import generate_recommendations


router = APIRouter(
    prefix="/api/analytics",
    tags=["Root Cause Analysis"]
)


# ============================================================
# ROOT CAUSE + STRATEGIC RECOMMENDATIONS
# ============================================================

@router.get("/root-cause")
def get_root_cause(
    product_id: str,
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):

    query = text("""
        SELECT
            p.product_id,
            p.product_name,
            p.category,

            COALESCE(SUM(oi.revenue), 0) AS revenue,

            COALESCE(SUM(oi.profit), 0) AS profit,

            COALESCE(SUM(oi.cost), 0) AS cost,

            COALESCE(
                SUM(
                    oi.unit_price
                    * oi.quantity
                    * oi.discount_percent / 100
                ),
                0
            ) AS discount,

            COALESCE(
                SUM(r.refund_amount),
                0
            ) AS returns

        FROM products p

        JOIN order_items oi
            ON p.product_id = oi.product_id

        JOIN orders o
            ON oi.order_id = o.order_id

        LEFT JOIN returns r
            ON r.product_id = oi.product_id
            AND r.order_id = oi.order_id

        WHERE p.product_id = :product_id

          AND o.order_status = 'Delivered'

          AND o.order_date >= :start_date

          AND o.order_date < :end_date + INTERVAL '1 day'

        GROUP BY
            p.product_id,
            p.product_name,
            p.category
    """)

    # --------------------------------------------------------
    # Execute database query
    # --------------------------------------------------------

    row = db.execute(
        query,
        {
            "product_id": product_id,
            "start_date": start_date,
            "end_date": end_date
        }
    ).mappings().first()


    # --------------------------------------------------------
    # No data found
    # --------------------------------------------------------

    if not row:
        return {
            "period": {
                "start_date": str(start_date),
                "end_date": str(end_date)
            },
            "product_id": product_id,
            "message": (
                "No product data found for the selected period."
            )
        }


    # --------------------------------------------------------
    # Calculate profitability
    # --------------------------------------------------------

    revenue = float(row["revenue"])
    profit = float(row["profit"])
    cost = float(row["cost"])
    discount = float(row["discount"])
    returns = float(row["returns"])


    if revenue > 0:
        margin = (profit / revenue) * 100
    else:
        margin = 0


    # --------------------------------------------------------
    # Prepare product data for agents
    # --------------------------------------------------------

    product = {
        "product_id": row["product_id"],

        "product_name": row["product_name"],

        "category": row["category"],

        "revenue": revenue,

        "profit": profit,

        "cost": cost,

        "discount": discount,

        "returns": returns,

        "profit_margin_percent": margin
    }


    # --------------------------------------------------------
    # Run Root Cause Agent
    # --------------------------------------------------------

    analysis = analyze_root_cause(product)


    # --------------------------------------------------------
    # Run Strategic Recommendation Agent
    # --------------------------------------------------------

    recommendations = generate_recommendations(
        product,
        analysis
    )


    # --------------------------------------------------------
    # Executive response
    # --------------------------------------------------------

    return {
        "period": {
            "start_date": str(start_date),
            "end_date": str(end_date)
        },

        "product": product,

        "root_cause_analysis": analysis,

        "strategic_recommendations": recommendations
    }