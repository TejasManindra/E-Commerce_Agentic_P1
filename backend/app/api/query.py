from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.agents.query_understanding_agent import (
    understand_query
)

from app.agents.marketing_agent import (
    analyze_marketing_performance,
    generate_marketing_recommendations
)

from app.agents.sql_generation_agent import (
    generate_sql,
    generate_root_cause_sql,
    generate_marketing_sql
)

from app.agents.analysis_agent import (
    analyze_query_result,
    analyze_root_cause
)

from app.agents.recommendation_agent import (
    generate_query_recommendations,
    generate_root_cause_recommendations
)

from app.agents.strategy_agent import (
    generate_strategic_strategies,
    generate_strategy_summary
)

from app.agents.cross_domain_agent import (
    analyze_cross_domain,
    generate_cross_domain_recommendations
)


router = APIRouter(
    prefix="/api/agent",
    tags=["Agentic BI"]
)


class BusinessQueryRequest(BaseModel):

    question: str = Field(
        ...,
        min_length=3
    )

    start_date: date

    end_date: date


@router.post("/ask")
def ask_business_question(
    request: BusinessQueryRequest,
    db: Session = Depends(get_db)
):

    # ---------------------------------------------------------
    # 1. VALIDATE DATE RANGE
    # ---------------------------------------------------------

    if request.start_date > request.end_date:

        return {
            "error": (
                "start_date must be before end_date"
            )
        }

    # ---------------------------------------------------------
    # 2. UNDERSTAND USER QUESTION
    # ---------------------------------------------------------

    intent = understand_query(
        request.question,
        request.start_date,
        request.end_date
    )

# ============================================================
# MARKETING-SPECIFIC QUERY
# ============================================================

    if intent.intent in {
        "marketing_analysis",
        "marketing_channel_analysis",
        "marketing_channel_comparison",
    }:

        marketing_sql, marketing_params = (
            generate_marketing_sql(
                request.start_date,
                request.end_date
            )
        )

        marketing_result = db.execute(
            text(marketing_sql),
            marketing_params
        )

        marketing_rows = [
            dict(row)
            for row in marketing_result.mappings().all()
        ]

        marketing_analysis = (
            analyze_marketing_performance(
                marketing_rows
            )
        )

        marketing_recommendations = (
            generate_marketing_recommendations(
                marketing_analysis
            )
        )

        requested_channel = None

        if intent.filters:

            requested_channel = (
                intent.filters.get(
                    "channel"
                )
            )

        if requested_channel:

            filtered_channels = [
                row
                for row in marketing_analysis.get(
                    "channels",
                    []
                )
                if str(
                    row.get(
                        "channel",
                        ""
                    )
                ).lower()
                == requested_channel.lower()
            ]

            marketing_analysis = {
                **marketing_analysis,
                "requested_channel":
                    requested_channel,
                "requested_channel_data":
                    filtered_channels[0]
                    if filtered_channels
                    else None,
            }

        return {
            "question":
                request.question,

            "intent": {
                "type":
                    intent.intent,

                "metric":
                    intent.metric,

                "dimension":
                    intent.dimension,

                "comparison":
                    intent.comparison,

                "filters":
                    intent.filters,
            },

            "marketing": {
                "analysis":
                    marketing_analysis,

                "recommendations":
                    marketing_recommendations,
            },

            "data":
                marketing_rows,
        }


    # ============================================================
    # NORMAL BUSINESS QUERY
    # ============================================================

    sql, params = generate_sql(
        intent
    )

    # ---------------------------------------------------------
    # 4. EXECUTE MAIN SQL
    # ---------------------------------------------------------

    result = db.execute(
        text(sql),
        params
    )

    rows = [
        dict(row)
        for row in result.mappings().all()
    ]

    # ---------------------------------------------------------
    # 5. ANALYZE MAIN RESULT
    # ---------------------------------------------------------

    analysis = analyze_query_result(
        intent,
        rows
    )

    # ---------------------------------------------------------
    # INITIALIZE OUTPUTS
    # ---------------------------------------------------------

    root_cause = None

    recommendations = []

    strategies = []

    strategy_summary = None

    # ---------------------------------------------------------
    # 6. ROOT CAUSE + RECOMMENDATION + STRATEGY
    # ---------------------------------------------------------

    if intent.comparison == "previous_period":

        # -----------------------------------------------------
        # 6.1 ROOT CAUSE SQL
        # -----------------------------------------------------

        root_sql, root_params = (
            generate_root_cause_sql(
                request.start_date,
                request.end_date
            )
        )

        root_result = db.execute(
            text(root_sql),
            root_params
        )

        root_rows = [
            dict(row)
            for row in root_result.mappings().all()
        ]

        # -----------------------------------------------------
        # 6.2 ROOT CAUSE ANALYSIS
        # -----------------------------------------------------

        root_cause = analyze_root_cause(
            root_rows
        )

        # -----------------------------------------------------
        # 6.3 EXISTING RECOMMENDATIONS
        # -----------------------------------------------------

        recommendations = (
            generate_root_cause_recommendations(
                root_cause
            )
        )

        # -----------------------------------------------------
        # 6.4 STRATEGY AGENT
        # -----------------------------------------------------

        strategies = (
            generate_strategic_strategies(
                root_cause
            )
        )

        strategy_summary = (
            generate_strategy_summary(
                strategies
            )
        )

    else:

        # -----------------------------------------------------
        # 6.5 NORMAL QUERY RECOMMENDATIONS
        # -----------------------------------------------------

        recommendations = (
            generate_query_recommendations(
                intent,
                analysis
            )
        )

    # ---------------------------------------------------------
    # 7. MARKETING INTELLIGENCE
    # ---------------------------------------------------------

    marketing_sql, marketing_params = (
        generate_marketing_sql(
            request.start_date,
            request.end_date
        )
    )

    marketing_result = db.execute(
        text(marketing_sql),
        marketing_params
    )

    marketing_rows = [
        dict(row)
        for row in marketing_result.mappings().all()
    ]

    # ---------------------------------------------------------
    # 8. MARKETING ANALYSIS
    # ---------------------------------------------------------

    marketing_analysis = (
        analyze_marketing_performance(
            marketing_rows
        )
    )

    # ---------------------------------------------------------
    # 9. MARKETING RECOMMENDATIONS
    # ---------------------------------------------------------

    marketing_recommendations = (
        generate_marketing_recommendations(
            marketing_analysis
        )
    )

    # ---------------------------------------------------------
    # 10. CROSS-DOMAIN ANALYSIS
    # ---------------------------------------------------------

    marketing_context = {
        "analysis": marketing_analysis,
        "recommendations": marketing_recommendations
    }

    cross_domain_analysis = (
        analyze_cross_domain(
            root_cause or {},
            marketing_context
        )
    )

    # ---------------------------------------------------------
    # 11. CROSS-DOMAIN RECOMMENDATIONS
    # ---------------------------------------------------------

    cross_domain_recommendations = (
        generate_cross_domain_recommendations(
            cross_domain_analysis
        )
    )

    # ---------------------------------------------------------
    # 12. RETURN COMPLETE AGENTIC RESPONSE
    # ---------------------------------------------------------

    return {

        "question": request.question,

        "intent": {
            "type": intent.intent,
            "metric": intent.metric,
            "dimension": intent.dimension,
            "comparison": intent.comparison
        },

        # Main business analysis
        "analysis": analysis,

        # Root cause analysis
        "root_cause": root_cause,

        # Main recommendations
        "recommendations": recommendations,

        # Strategic business focus
        "strategies": strategies,

        "strategy_summary": strategy_summary,

        # Marketing intelligence
        "marketing": {

            "analysis": marketing_analysis,

            "recommendations":
                marketing_recommendations
        },

        # Cross-domain intelligence
        "cross_domain": {

            "analysis":
                cross_domain_analysis,

            "recommendations":
                cross_domain_recommendations
        },

        # Main query data
        "data": rows
    }