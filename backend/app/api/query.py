from datetime import date
from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text

from app.agents.query_understanding_agent import (
    understand_query,
)

from app.agents.sql_generation_agent import (
    generate_sql,
    generate_root_cause_sql,
    generate_marketing_sql,
)

from app.agents.analysis_agent import (
    analyze_query_result,
    analyze_root_cause,
)

from app.agents.marketing_agent import (
    analyze_marketing_performance,
    generate_marketing_recommendations,
)

from app.agents.recommendation_agent import (
    generate_query_recommendations,
    generate_root_cause_recommendations,
)

from app.agents.strategy_agent import (
    generate_strategic_strategies,
    generate_strategy_summary,
)

from app.agents.cross_domain_agent import (
    analyze_cross_domain,
    generate_cross_domain_recommendations,
)

from app.agents.orchestrator_agent import (
    OrchestratorAgent,
)

from app.database.database import SessionLocal


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/agent",
    tags=["Agentic AI"],
)


# ============================================================
# ORCHESTRATOR
# ============================================================

orchestrator = OrchestratorAgent()


# ============================================================
# REQUEST MODEL
# ============================================================

class AgentQueryRequest(BaseModel):
    question: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None


# ============================================================
# SQL EXECUTION
# ============================================================

def execute_sql(sql: str) -> list:
    """
    Execute generated SQL against PostgreSQL.
    """

    db = SessionLocal()

    try:
        result = db.execute(
            text(sql)
        )

        rows = result.mappings().all()

        return [
            dict(row)
            for row in rows
        ]

    finally:
        db.close()


# ============================================================
# MULTI-PERIOD ANALYSIS
# ============================================================

def analyze_multi_period_result(
    rows: list,
    metric: str,
) -> Dict[str, Any]:
    """
    Analyze multi-period results.

    Example:

        month     value
        2026-06   100
        2026-07   120
        2026-08    90

    The analysis detects:

    - overall change
    - month-to-month changes
    - increasing trend
    - declining trend
    - stable trend
    - volatile trend
    - largest growth
    - largest decline
    - highest period
    - lowest period
    """

    # --------------------------------------------------------
    # No data
    # --------------------------------------------------------

    if not rows:

        return {
            "metric": metric,
            "period_count": 0,
            "monthly_values": [],
            "trend": "no_data",
            "trend_strength": "none",
            "insights": [
                "No data was available for the requested periods."
            ],
        }

    # --------------------------------------------------------
    # Prepare monthly values
    # --------------------------------------------------------

    monthly_values = []

    for row in rows:

        month = row.get(
            "month"
        )

        value = row.get(
            "value",
            0,
        )

        if value is None:
            value = 0

        try:
            numeric_value = float(
                value
            )

        except (
            TypeError,
            ValueError,
        ):
            numeric_value = 0.0

        monthly_values.append(
            {
                "month": str(
                    month
                ),

                "value": numeric_value,
            }
        )

    # --------------------------------------------------------
    # Sort chronologically
    # --------------------------------------------------------

    monthly_values.sort(
        key=lambda item: item["month"]
    )

    # --------------------------------------------------------
    # First and latest values
    # --------------------------------------------------------

    first_value = (
        monthly_values[0]["value"]
    )

    latest_value = (
        monthly_values[-1]["value"]
    )

    # --------------------------------------------------------
    # Overall change
    # --------------------------------------------------------

    overall_change = (
        latest_value
        - first_value
    )

    # --------------------------------------------------------
    # Overall percentage change
    # --------------------------------------------------------

    if first_value != 0:

        overall_change_percent = (
            overall_change
            / abs(first_value)
        ) * 100

    else:

        overall_change_percent = None

    # ========================================================
    # PERIOD-TO-PERIOD MOVEMENTS
    # ========================================================

    period_changes = []

    for index in range(
        1,
        len(monthly_values),
    ):

        previous = (
            monthly_values[
                index - 1
            ]
        )

        current = (
            monthly_values[
                index
            ]
        )

        change = (
            current["value"]
            - previous["value"]
        )

        if previous["value"] != 0:

            change_percent = (
                change
                / abs(
                    previous["value"]
                )
            ) * 100

        else:

            change_percent = None

        period_changes.append(
            {
                "from_month":
                    previous["month"],

                "to_month":
                    current["month"],

                "change":
                    change,

                "change_percent":
                    change_percent,
            }
        )

    # ========================================================
    # POSITIVE / NEGATIVE MOVEMENTS
    # ========================================================

    positive_movements = [
        item
        for item in period_changes
        if item["change"] > 0
    ]

    negative_movements = [
        item
        for item in period_changes
        if item["change"] < 0
    ]

    # ========================================================
    # LARGEST DECLINE
    # ========================================================

    largest_decline = None

    if negative_movements:

        largest_decline = min(
            negative_movements,
            key=lambda item: item[
                "change"
            ],
        )

    # ========================================================
    # LARGEST GROWTH
    # ========================================================

    largest_growth = None

    if positive_movements:

        largest_growth = max(
            positive_movements,
            key=lambda item: item[
                "change"
            ],
        )

    # ========================================================
    # HIGHEST PERIOD
    # ========================================================

    highest_period = max(
        monthly_values,
        key=lambda item: item[
            "value"
        ],
    )

    # ========================================================
    # LOWEST PERIOD
    # ========================================================

    lowest_period = min(
        monthly_values,
        key=lambda item: item[
            "value"
        ],
    )

    # ========================================================
    # TREND
    #
    # Do not rely only on first -> last.
    #
    # Example:
    #
    # June   100
    # July   80
    # August 100
    #
    # First -> last = 0
    #
    # But actual pattern:
    #
    # 100 -> 80 -> 100
    #
    # This is volatile, not necessarily stable.
    # ========================================================

    if not period_changes:

        trend = "stable"

    elif (
        len(negative_movements)
        > len(positive_movements)
    ):

        trend = "declining"

    elif (
        len(positive_movements)
        > len(negative_movements)
    ):

        trend = "increasing"

    elif overall_change > 0:

        trend = "increasing"

    elif overall_change < 0:

        trend = "declining"

    else:

        trend = "stable"

    # ========================================================
    # TREND STRENGTH
    # ========================================================

    if not period_changes:

        trend_strength = (
            "insufficient_data"
        )

    elif (
        len(negative_movements)
        == len(period_changes)
    ):

        trend_strength = (
            "strong_decline"
        )

    elif (
        len(positive_movements)
        == len(period_changes)
    ):

        trend_strength = (
            "strong_growth"
        )

    elif (
        positive_movements
        and negative_movements
    ):

        trend_strength = (
            "volatile"
        )

    else:

        trend_strength = (
            "stable"
        )

    # ========================================================
    # INSIGHTS
    # ========================================================

    metric_name = (
        metric
        .replace(
            "_",
            " ",
        )
        .title()
    )

    insights = []

    # --------------------------------------------------------
    # Overall movement
    # --------------------------------------------------------

    if overall_change_percent is not None:

        if overall_change_percent > 0:

            insights.append(
                f"{metric_name} increased by "
                f"{overall_change_percent:.2f}% "
                f"from the first to the latest period."
            )

        elif overall_change_percent < 0:

            insights.append(
                f"{metric_name} decreased by "
                f"{abs(overall_change_percent):.2f}% "
                f"from the first to the latest period."
            )

        else:

            insights.append(
                f"{metric_name} ended at the same level "
                f"as the first selected period."
            )

    # --------------------------------------------------------
    # Trend interpretation
    # --------------------------------------------------------

    if trend == "declining":

        insights.append(
            f"The overall period pattern indicates "
            f"a declining trend."
        )

    elif trend == "increasing":

        insights.append(
            f"The overall period pattern indicates "
            f"an increasing trend."
        )

    elif trend_strength == "volatile":

        insights.append(
            f"{metric_name} shows volatility across "
            f"the selected periods rather than a "
            f"consistent directional trend."
        )

    else:

        insights.append(
            f"{metric_name} remained broadly stable "
            f"across the selected periods."
        )

    # --------------------------------------------------------
    # Largest decline insight
    # --------------------------------------------------------

    if largest_decline:

        if (
            largest_decline[
                "change_percent"
            ]
            is not None
        ):

            insights.append(
                f"The largest decline occurred from "
                f"{largest_decline['from_month']} "
                f"to "
                f"{largest_decline['to_month']}, "
                f"with a movement of "
                f"{abs(largest_decline['change_percent']):.2f}%."
            )

        else:

            insights.append(
                f"The largest decline occurred from "
                f"{largest_decline['from_month']} "
                f"to "
                f"{largest_decline['to_month']}."
            )

    # --------------------------------------------------------
    # Largest growth insight
    # --------------------------------------------------------

    if largest_growth:

        if (
            largest_growth[
                "change_percent"
            ]
            is not None
        ):

            insights.append(
                f"The largest growth occurred from "
                f"{largest_growth['from_month']} "
                f"to "
                f"{largest_growth['to_month']}, "
                f"with a movement of "
                f"{largest_growth['change_percent']:.2f}%."
            )

        else:

            insights.append(
                f"The largest growth occurred from "
                f"{largest_growth['from_month']} "
                f"to "
                f"{largest_growth['to_month']}."
            )

    # ========================================================
    # FINAL MULTI-PERIOD RESULT
    # ========================================================

    return {

        "metric":
            metric,

        "period_count":
            len(monthly_values),

        "monthly_values":
            monthly_values,

        "first_period":
            monthly_values[0],

        "latest_period":
            monthly_values[-1],

        "first_value":
            first_value,

        "latest_value":
            latest_value,

        "change":
            overall_change,

        "change_percent":
            overall_change_percent,

        "trend":
            trend,

        "trend_strength":
            trend_strength,

        "highest_period":
            highest_period,

        "lowest_period":
            lowest_period,

        "period_changes":
            period_changes,

        "positive_movements":
            len(
                positive_movements
            ),

        "negative_movements":
            len(
                negative_movements
            ),

        "largest_decline":
            largest_decline,

        "largest_growth":
            largest_growth,

        "insights":
            insights,
    }


# ============================================================
# MAIN AGENT ENDPOINT
# ============================================================

@router.post("/ask")
def ask_agent(
    request: AgentQueryRequest,
):

    # ========================================================
    # VALIDATE QUESTION
    # ========================================================

    question = (
        request.question.strip()
    )

    if not question:

        return {
            "status": "error",
            "message": (
                "Question cannot be empty."
            ),
        }

    # ========================================================
    # VALIDATE DATES
    # ========================================================

    if (
        request.start_date
        and request.end_date
        and request.start_date
        > request.end_date
    ):

        return {
            "status": "error",
            "message": (
                "start_date cannot be later "
                "than end_date."
            ),
        }

    # ========================================================
    # QUERY UNDERSTANDING
    # ========================================================

    intent = understand_query(
        question,
        request.start_date,
        request.end_date,
    )

    # ========================================================
    # CREATE ORCHESTRATION PLAN
    # ========================================================

    orchestration_plan = (
        orchestrator.create_plan(
            intent
        )
    )

    # ========================================================
    # SHARED STATE
    # ========================================================

    state: Dict[str, Any] = {

        "intent":
            intent,

        "analysis":
            None,

        "root_cause":
            None,

        "marketing":
            None,

        "cross_domain":
            None,

        "recommendations":
            None,

        "strategies":
            None,

        "strategy_summary":
            None,

        "data":
            [],
    }

    # ========================================================
    # ANALYSIS STAGE
    # ========================================================

    def run_analysis():

        sql = generate_sql(
            intent
        )

        rows = execute_sql(
            sql
        )

        # ----------------------------------------------------
        # Multi-period analysis
        # ----------------------------------------------------

        if (
            intent.comparison
            == "previous_periods"
        ):

            result = (
                analyze_multi_period_result(
                    rows,
                    intent.metric,
                )
            )

        else:

            result = (
                analyze_query_result(
                    rows,
                    intent,
                )
            )

        state[
            "analysis"
        ] = result

        state[
            "data"
        ] = rows

        return result

    # ========================================================
    # ROOT CAUSE STAGE
    # ========================================================

    def run_root_cause():

        if (
            not request.start_date
            or not request.end_date
        ):

            return {
                "status":
                    "skipped",

                "reason":
                    (
                        "Start and end dates are required "
                        "for root cause analysis."
                    ),
            }

        sql = generate_root_cause_sql(
            request.start_date,
            request.end_date,
        )

        rows = execute_sql(
            sql
        )

        result = analyze_root_cause(
            rows
        )

        recommendations = (
            generate_root_cause_recommendations(
                result
            )
        )

        state[
            "root_cause"
        ] = {

            "analysis":
                result,

            "recommendations":
                recommendations,
        }

        return state[
            "root_cause"
        ]

    # ========================================================
    # MARKETING STAGE
    # ========================================================

    def run_marketing():

        if (
            not request.start_date
            or not request.end_date
        ):

            return {
                "status":
                    "skipped",

                "reason":
                    (
                        "Start and end dates are required "
                        "for marketing analysis."
                    ),
            }

        sql = generate_marketing_sql(
            request.start_date,
            request.end_date,
        )

        rows = execute_sql(
            sql
        )

        analysis = (
            analyze_marketing_performance(
                rows
            )
        )

        recommendations = (
            generate_marketing_recommendations(
                analysis
            )
        )

        state[
            "marketing"
        ] = {

            "analysis":
                analysis,

            "recommendations":
                recommendations,

            "data":
                rows,
        }

        return state[
            "marketing"
        ]

    # ========================================================
    # CROSS DOMAIN STAGE
    # ========================================================

    def run_cross_domain():

        root_cause = (
            state.get(
                "root_cause"
            )
        )

        marketing = (
            state.get(
                "marketing"
            )
        )

        if (
            not root_cause
            and not marketing
        ):

            return {
                "status":
                    "skipped",

                "reason":
                    (
                        "Cross-domain analysis requires "
                        "root-cause or marketing evidence."
                    ),
            }

        root_cause_analysis = (
            root_cause.get(
                "analysis"
            )
            if root_cause
            else None
        )

        marketing_analysis = (
            marketing.get(
                "analysis"
            )
            if marketing
            else None
        )

        result = analyze_cross_domain(
            root_cause_analysis,
            marketing_analysis,
        )

        recommendations = (
            generate_cross_domain_recommendations(
                result
            )
        )

        state[
            "cross_domain"
        ] = {

            "analysis":
                result,

            "recommendations":
                recommendations,
        }

        return state[
            "cross_domain"
        ]

    # ========================================================
    # RECOMMENDATION STAGE
    # ========================================================

    def run_recommendation():

        # ====================================================
        # MULTI-PERIOD TREND
        # ====================================================

        if (
            intent.comparison
            == "previous_periods"
        ):

            analysis = (
                state.get(
                    "analysis"
                )
                or {}
            )

            recommendations = []

            trend = analysis.get(
                "trend"
            )

            trend_strength = (
                analysis.get(
                    "trend_strength"
                )
            )

            largest_decline = (
                analysis.get(
                    "largest_decline"
                )
            )

            largest_growth = (
                analysis.get(
                    "largest_growth"
                )
            )

            # ------------------------------------------------
            # DECLINING
            # ------------------------------------------------

            if trend == "declining":

                if largest_decline:

                    recommendations.append(
                        {
                            "priority":
                                "High",

                            "action":
                                (
                                    "Investigate the largest "
                                    "period-over-period decline."
                                ),

                            "reason":
                                (
                                    f"The largest decline occurred "
                                    f"from "
                                    f"{largest_decline['from_month']} "
                                    f"to "
                                    f"{largest_decline['to_month']}."
                                ),
                        }
                    )

                recommendations.append(
                    {
                        "priority":
                            "Medium",

                        "action":
                            (
                                "Review category, pricing, "
                                "discount, return and order "
                                "trends during the declining periods."
                            ),

                        "reason":
                            (
                                "The multi-period analysis "
                                "indicates a declining "
                                "business trend."
                            ),
                    }
                )

            # ------------------------------------------------
            # INCREASING
            # ------------------------------------------------

            elif trend == "increasing":

                recommendations.append(
                    {
                        "priority":
                            "High",

                        "action":
                            (
                                "Investigate and scale the "
                                "drivers behind the positive trend."
                            ),

                        "reason":
                            (
                                "The selected periods indicate "
                                "an improving business trend."
                            ),
                    }
                )

                if largest_growth:

                    recommendations.append(
                        {
                            "priority":
                                "Medium",

                            "action":
                                (
                                    "Examine the strongest "
                                    "growth period and identify "
                                    "repeatable business drivers."
                                ),

                            "reason":
                                (
                                    f"The largest growth occurred "
                                    f"from "
                                    f"{largest_growth['from_month']} "
                                    f"to "
                                    f"{largest_growth['to_month']}."
                                ),
                        }
                    )

            # ------------------------------------------------
            # VOLATILE
            # ------------------------------------------------

            elif (
                trend_strength
                == "volatile"
            ):

                recommendations.append(
                    {
                        "priority":
                            "High",

                        "action":
                            (
                                "Investigate the periods with "
                                "the largest increases and declines "
                                "before making major strategic changes."
                            ),

                        "reason":
                            (
                                "The metric is volatile across "
                                "the selected periods rather than "
                                "following a consistent trend."
                            ),
                    }
                )

                if largest_decline:

                    recommendations.append(
                        {
                            "priority":
                                "Medium",

                            "action":
                                (
                                    "Investigate the business "
                                    "drivers behind the largest decline."
                                ),

                            "reason":
                                (
                                    f"The sharpest decline occurred "
                                    f"from "
                                    f"{largest_decline['from_month']} "
                                    f"to "
                                    f"{largest_decline['to_month']}."
                                ),
                        }
                    )

            # ------------------------------------------------
            # STABLE
            # ------------------------------------------------

            else:

                recommendations.append(
                    {
                        "priority":
                            "Medium",

                        "action":
                            (
                                "Maintain the current operating "
                                "strategy while monitoring "
                                "month-to-month performance "
                                "for emerging changes."
                            ),

                        "reason":
                            (
                                "The selected periods do not show "
                                "a significant directional movement."
                            ),
                    }
                )

            state[
                "recommendations"
            ] = recommendations

            return recommendations

        # ====================================================
        # ROOT CAUSE RECOMMENDATIONS
        # ====================================================

        root_cause = (
            state.get(
                "root_cause"
            )
        )

        if root_cause:

            recommendations = (
                root_cause.get(
                    "recommendations",
                    [],
                )
            )

            if recommendations:

                state[
                    "recommendations"
                ] = recommendations

                return recommendations

        # ====================================================
        # MARKETING RECOMMENDATIONS
        # ====================================================

        marketing = (
            state.get(
                "marketing"
            )
        )

        if marketing:

            recommendations = (
                marketing.get(
                    "recommendations",
                    [],
                )
            )

            if recommendations:

                state[
                    "recommendations"
                ] = recommendations

                return recommendations

            marketing_analysis = (
                marketing.get(
                    "analysis",
                    {},
                )
            )

            recommendations = (
                generate_query_recommendations(
                    intent,
                    marketing_analysis,
                )
            )

            state[
                "recommendations"
            ] = recommendations

            return recommendations

        # ====================================================
        # CROSS DOMAIN RECOMMENDATIONS
        # ====================================================

        cross_domain = (
            state.get(
                "cross_domain"
            )
        )

        if cross_domain:

            recommendations = (
                cross_domain.get(
                    "recommendations",
                    [],
                )
            )

            if recommendations:

                state[
                    "recommendations"
                ] = recommendations

                return recommendations

        # ====================================================
        # GENERIC RECOMMENDATIONS
        # ====================================================

        analysis = (
            state.get(
                "analysis"
            )
        )

        recommendations = (
            generate_query_recommendations(
                intent,
                analysis,
            )
        )

        state[
            "recommendations"
        ] = recommendations

        return recommendations

    # ========================================================
    # STRATEGY STAGE
    # ========================================================

    def run_strategy():

        root_cause = (
            state.get(
                "root_cause"
            )
        )

        if not root_cause:

            return {
                "status":
                    "skipped",

                "reason":
                    (
                        "Strategic prioritization requires "
                        "root-cause evidence."
                    ),
            }

        root_cause_analysis = (
            root_cause.get(
                "analysis"
            )
        )

        if not root_cause_analysis:

            return {
                "status":
                    "skipped",

                "reason":
                    (
                        "Root-cause analysis is not available "
                        "for strategic prioritization."
                    ),
            }

        # ----------------------------------------------------
        # YOUR ACTUAL STRATEGY AGENT
        # ----------------------------------------------------

        strategies = (
            generate_strategic_strategies(
                root_cause_analysis
            )
        )

        summary = (
            generate_strategy_summary(
                strategies
            )
        )

        state[
            "strategies"
        ] = strategies

        state[
            "strategy_summary"
        ] = summary

        return {

            "strategies":
                strategies,

            "summary":
                summary,
        }

    # ========================================================
    # STAGE FUNCTIONS
    # ========================================================

    stage_functions = {

        "analysis":
            run_analysis,

        "root_cause":
            run_root_cause,

        "marketing":
            run_marketing,

        "cross_domain":
            run_cross_domain,

        "recommendation":
            run_recommendation,

        "strategy":
            run_strategy,
    }

    # ========================================================
    # EXECUTE ORCHESTRATED PLAN
    # ========================================================

    execution_results = (
        orchestrator.execute_plan(
            orchestration_plan,
            stage_functions,
        )
    )

    # ========================================================
    # EVIDENCE EVALUATION
    # ========================================================

    evidence = (
        orchestrator.evaluate_evidence(
            intent,
            execution_results,
        )
    )

    # ========================================================
    # REPLANNING
    # ========================================================

    replan = None

    if orchestrator.should_replan(
        evidence
    ):

        replan = (
            orchestrator.create_replan(
                intent,
                evidence,
            )
        )

    # ========================================================
    # ORCHESTRATION METADATA
    # ========================================================

    orchestration_metadata = (
        execution_results.get(
            "_orchestration",
            {},
        )
    )

    executed_stages = (
        orchestration_metadata.get(
            "executed_stages",
            [],
        )
    )

    failed_stages = (
        orchestration_metadata.get(
            "failed_stages",
            [],
        )
    )

    skipped_stages = (
        orchestration_metadata.get(
            "skipped_stages",
            [],
        )
    )

    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    return {

        "status":
            "success",

        # ----------------------------------------------------
        # QUESTION
        # ----------------------------------------------------

        "question":
            question,

        # ----------------------------------------------------
        # INTENT
        # ----------------------------------------------------

        "intent": {

            "original_question":
                intent.original_question,

            "intent":
                intent.intent,

            "metric":
                intent.metric,

            "dimension":
                intent.dimension,

            "start_date":
                (
                    str(
                        intent.start_date
                    )
                    if intent.start_date
                    else None
                ),

            "end_date":
                (
                    str(
                        intent.end_date
                    )
                    if intent.end_date
                    else None
                ),

            "comparison":
                intent.comparison,

            "period_count":
                getattr(
                    intent,
                    "period_count",
                    None,
                ),

            "filters":
                intent.filters,
        },

        # ----------------------------------------------------
        # ORCHESTRATION
        # ----------------------------------------------------

        "orchestration": {

            "objective":
                orchestration_plan.get(
                    "objective"
                ),

            "planned_stages":
                orchestration_plan.get(
                    "plan",
                    [],
                ),

            "executed_stages":
                executed_stages,

            "failed_stages":
                failed_stages,

            "skipped_stages":
                skipped_stages,

            "reasoning":
                orchestration_plan.get(
                    "reasoning",
                    [],
                ),
        },

        # ----------------------------------------------------
        # ANALYSIS
        # ----------------------------------------------------

        "analysis":
            state.get(
                "analysis"
            ),

        # ----------------------------------------------------
        # ROOT CAUSE
        # ----------------------------------------------------

        "root_cause":
            state.get(
                "root_cause"
            ),

        # ----------------------------------------------------
        # MARKETING
        # ----------------------------------------------------

        "marketing":
            state.get(
                "marketing"
            ),

        # ----------------------------------------------------
        # CROSS DOMAIN
        # ----------------------------------------------------

        "cross_domain":
            state.get(
                "cross_domain"
            ),

        # ----------------------------------------------------
        # RECOMMENDATIONS
        # ----------------------------------------------------

        "recommendations":
            state.get(
                "recommendations"
            ),

        # ----------------------------------------------------
        # STRATEGIES
        # ----------------------------------------------------

        "strategies":
            state.get(
                "strategies"
            ),

        # ----------------------------------------------------
        # STRATEGY SUMMARY
        # ----------------------------------------------------

        "strategy_summary":
            state.get(
                "strategy_summary"
            ),

        # ----------------------------------------------------
        # RAW DATA
        # ----------------------------------------------------

        "data":
            state.get(
                "data",
                [],
            ),

        # ----------------------------------------------------
        # EVIDENCE
        # ----------------------------------------------------

        "evidence":
            evidence,

        # ----------------------------------------------------
        # REPLAN
        # ----------------------------------------------------

        "replan":
            replan,
    }