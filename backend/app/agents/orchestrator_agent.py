from typing import Dict, Any, List


class OrchestratorAgent:
    """
    Coordinates the analytical agents required to answer
    a business question.

    Responsibilities:
    1. Understand the business objective
    2. Create an analytical plan
    3. Select required agents
    4. Execute selected analytical stages
    5. Evaluate collected evidence
    6. Determine whether additional analysis is required
    """

    def __init__(self):
        self.available_agents = {
            "query_understanding": "Query Understanding Agent",
            "analysis": "Analysis Agent",
            "root_cause": "Root Cause Agent",
            "marketing": "Marketing Agent",
            "recommendation": "Recommendation Agent",
            "strategy": "Strategy Agent",
            "cross_domain": "Cross-Domain Agent",
        }

    # =========================================================
    # 1. CREATE PLAN
    # =========================================================

    def create_plan(
        self,
        intent: Any
    ) -> Dict[str, Any]:

        intent_type = getattr(
            intent,
            "intent",
            ""
        )

        metric = getattr(
            intent,
            "metric",
            ""
        )

        comparison = getattr(
            intent,
            "comparison",
            None
        )

        plan: List[str] = []

        # -----------------------------------------------------
        # Base business analysis
        # -----------------------------------------------------

        plan.append("analysis")

        # -----------------------------------------------------
        # Root cause analysis
        # -----------------------------------------------------

        if comparison == "previous_period":
            plan.append("root_cause")

        # -----------------------------------------------------
        # Marketing analysis
        # -----------------------------------------------------

        if metric in {
            "roas",
            "cac",
            "conversion_rate"
        }:
            plan.append("marketing")

        if intent_type in {
            "marketing_analysis",
            "marketing_channel_analysis",
            "marketing_channel_comparison"
        }:
            plan.append("marketing")

        # -----------------------------------------------------
        # Cross-domain analysis
        # -----------------------------------------------------

        if (
            comparison == "previous_period"
            and metric in {
                "profit",
                "revenue",
                "orders",
                "customers"
            }
        ):
            plan.append("cross_domain")

        # -----------------------------------------------------
        # Recommendation
        # -----------------------------------------------------

        plan.append("recommendation")

        # -----------------------------------------------------
        # Strategy
        # -----------------------------------------------------

        if (
            comparison == "previous_period"
            or metric in {
                "profit",
                "revenue"
            }
        ):
            plan.append("strategy")

        # Remove duplicates while preserving order
        plan = list(dict.fromkeys(plan))

        return {
            "objective": self._determine_objective(
                intent
            ),
            "plan": plan,
            "reasoning": self._explain_plan(
                intent,
                plan
            )
        }

    # =========================================================
    # 2. EXECUTE PLAN
    # =========================================================

    def execute_plan(
        self,
        plan: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the selected analytical stages.

        The orchestrator does not contain the business
        calculations itself. Instead, it decides which
        existing analytical capabilities should execute.
        """

        results = {}

        selected_steps = plan.get(
            "plan",
            []
        )

        # -----------------------------------------------------
        # ANALYSIS
        # -----------------------------------------------------

        if "analysis" in selected_steps:

            analysis_function = context.get(
                "analysis_function"
            )

            if analysis_function:
                results["analysis"] = (
                    analysis_function()
                )

        # -----------------------------------------------------
        # ROOT CAUSE
        # -----------------------------------------------------

        if "root_cause" in selected_steps:

            root_cause_function = context.get(
                "root_cause_function"
            )

            if root_cause_function:
                results["root_cause"] = (
                    root_cause_function(
                        results.get(
                            "analysis"
                        )
                    )
                )

        # -----------------------------------------------------
        # MARKETING
        # -----------------------------------------------------

        if "marketing" in selected_steps:

            marketing_function = context.get(
                "marketing_function"
            )

            if marketing_function:
                results["marketing"] = (
                    marketing_function()
                )

        # -----------------------------------------------------
        # CROSS DOMAIN
        # -----------------------------------------------------

        if "cross_domain" in selected_steps:

            cross_domain_function = context.get(
                "cross_domain_function"
            )

            if cross_domain_function:

                results["cross_domain"] = (
                    cross_domain_function(
                        results.get(
                            "root_cause"
                        ),
                        results.get(
                            "marketing"
                        )
                    )
                )

        # -----------------------------------------------------
        # RECOMMENDATION
        # -----------------------------------------------------

        if "recommendation" in selected_steps:

            recommendation_function = context.get(
                "recommendation_function"
            )

            if recommendation_function:

                results["recommendations"] = (
                    recommendation_function(
                        results
                    )
                )

        # -----------------------------------------------------
        # STRATEGY
        # -----------------------------------------------------

        if "strategy" in selected_steps:

            strategy_function = context.get(
                "strategy_function"
            )

            if strategy_function:

                results["strategy"] = (
                    strategy_function(
                        results
                    )
                )

        return results

    # =========================================================
    # 3. DETERMINE OBJECTIVE
    # =========================================================

    def _determine_objective(
        self,
        intent: Any
    ) -> str:

        intent_type = getattr(
            intent,
            "intent",
            ""
        )

        if intent_type.endswith(
            "_decline_analysis"
        ):
            return (
                "Identify the drivers of business decline."
            )

        if intent_type.startswith(
            "marketing"
        ):
            return (
                "Evaluate marketing performance "
                "and identify actions."
            )

        if intent_type == (
            "product_performance_analysis"
        ):
            return (
                "Identify product-level "
                "performance opportunities."
            )

        if intent_type == (
            "category_revenue_analysis"
        ):
            return (
                "Evaluate category performance "
                "and business contribution."
            )

        if intent_type == (
            "geography_analysis"
        ):
            return (
                "Evaluate geographic business performance."
            )

        if intent_type == (
            "monthly_trend_analysis"
        ):
            return (
                "Identify important business trends over time."
            )

        return (
            "Analyze the requested business metric "
            "and provide actionable insight."
        )

    # =========================================================
    # 4. EXPLAIN PLAN
    # =========================================================

    def _explain_plan(
        self,
        intent: Any,
        plan: List[str]
    ) -> List[str]:

        explanations = []

        if "analysis" in plan:
            explanations.append(
                "Analyze the requested business metric."
            )

        if "root_cause" in plan:
            explanations.append(
                "Investigate drivers behind the "
                "period-over-period change."
            )

        if "marketing" in plan:
            explanations.append(
                "Evaluate marketing efficiency "
                "and channel performance."
            )

        if "cross_domain" in plan:
            explanations.append(
                "Compare business and marketing "
                "evidence for related signals."
            )

        if "recommendation" in plan:
            explanations.append(
                "Generate evidence-based "
                "management actions."
            )

        if "strategy" in plan:
            explanations.append(
                "Prioritize actions into "
                "strategic business priorities."
            )

        return explanations

    # =========================================================
    # 5. EVALUATE EVIDENCE
    # =========================================================

    def evaluate_evidence(
        self,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:

        evidence = []

        if results.get("analysis"):
            evidence.append(
                "business_analysis"
            )

        if results.get("root_cause"):
            evidence.append(
                "root_cause"
            )

        if results.get("marketing"):
            evidence.append(
                "marketing"
            )

        if results.get("cross_domain"):
            evidence.append(
                "cross_domain"
            )

        sufficient = (
            "business_analysis"
            in evidence
        )

        if (
            results.get("root_cause")
            and isinstance(
                results["root_cause"],
                dict
            )
        ):
            sufficient = True

        missing = []

        if not sufficient:
            missing.append(
                "additional business analysis"
            )

        return {
            "sufficient": sufficient,
            "evidence_available": evidence,
            "missing_information": missing
        }

    # =========================================================
    # 6. RE-PLANNING DECISION
    # =========================================================

    def should_replan(
        self,
        evaluation: Dict[str, Any]
    ) -> bool:

        return not evaluation.get(
            "sufficient",
            False
        )


# =============================================================
# FACTORY
# =============================================================

def create_orchestrator() -> OrchestratorAgent:

    return OrchestratorAgent()