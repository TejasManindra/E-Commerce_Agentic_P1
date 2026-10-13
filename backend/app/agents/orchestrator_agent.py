from typing import Any, Callable, Dict, List


class OrchestratorAgent:
    """
    Orchestrator Agent

    Responsibilities:
    1. Understand the analytical requirement received from Query Understanding.
    2. Dynamically create an execution plan.
    3. Execute only the required analytical stages.
    4. Track successful / failed / skipped stages.
    5. Evaluate whether the available evidence is sufficient.
    6. Support re-planning when additional analysis is required.
    """

    def __init__(self):
        self.available_agents = {
            "analysis": "Data Analysis Agent",
            "root_cause": "Root Cause Analysis Agent",
            "marketing": "Marketing Analysis Agent",
            "cross_domain": "Cross-Domain Analysis Agent",
            "recommendation": "Recommendation Agent",
            "strategy": "Strategy Agent",
        }

    # ============================================================
    # PLAN CREATION
    # ============================================================

    def create_plan(self, intent) -> Dict[str, Any]:
        """
        Dynamically create an execution plan based on QueryIntent.
        """

        question = (intent.original_question or "").lower()

        comparison_requested = (
            intent.comparison in {
                "previous_period",
                "previous_periods",
                "month_over_month",
                "week_over_week",
                "year_over_year",
            }
            or any(
                phrase in question
                for phrase in [
                    "previous",
                    "prior",
                    "last month",
                    "last week",
                    "last year",
                    "previous month",
                    "previous week",
                    "previous year",
                    "mom",
                    "wow",
                    "yoy",
                    "compare",
                    "versus",
                    "vs",
                    "change from",
                ]
            )
        )

        multi_period_requested = (
            intent.comparison == "previous_periods"
            or getattr(intent, "period_count", None) is not None
        )

        category_requested = (
            intent.dimension == "category"
            or "category" in question
            or "categories" in question
        )

        marketing_requested = (
            intent.metric in {
                "roas",
                "cac",
                "conversion_rate",
            }
            or "marketing" in question
            or "campaign" in question
            or "advertising" in question
            or "ads" in question
            or "customer acquisition" in question
            or "acquisition efficiency" in question
            or intent.intent in {
                "marketing_analysis",
                "roas_analysis",
                "cac_analysis",
                "conversion_analysis",
            }
        )

        broad_business_question = (
            intent.metric in {
                "revenue",
                "profit",
                "orders",
                "customers",
            }
            and (
                intent.dimension is None
                or intent.dimension == "month"
            )
        )

        plan: List[str] = []

        # --------------------------------------------------------
        # Every business question starts with analytical retrieval
        # --------------------------------------------------------

        plan.append("analysis")

        # --------------------------------------------------------
        # MULTI-PERIOD TREND
        # Example:
        # "Show previous 3 months revenue"
        # --------------------------------------------------------

        if multi_period_requested:
            plan.append("recommendation")

            final_plan = list(dict.fromkeys(plan))

            return {
                "objective": self._determine_objective(intent),
                "plan": final_plan,
                "reasoning": self._explain_plan(
                    intent,
                    final_plan,
                ),
            }

        # --------------------------------------------------------
        # ROOT CAUSE
        # --------------------------------------------------------

        if comparison_requested:
            plan.append("root_cause")

        # --------------------------------------------------------
        # MARKETING
        # --------------------------------------------------------

        if marketing_requested:
            plan.append("marketing")

        # --------------------------------------------------------
        # CROSS DOMAIN
        #
        # Useful when the question involves:
        # - profit/revenue decline
        # - marketing + business performance
        # - category + marketing
        # - broad business questions
        # --------------------------------------------------------

        if comparison_requested and (
            intent.metric in {
                "profit",
                "revenue",
                "orders",
                "customers",
            }
            or broad_business_question
            or category_requested
            or marketing_requested
        ):
            plan.append("cross_domain")

        # --------------------------------------------------------
        # RECOMMENDATION
        # --------------------------------------------------------

        plan.append("recommendation")

        # --------------------------------------------------------
        # STRATEGY
        # --------------------------------------------------------

        if (
            comparison_requested
            or intent.metric in {
                "profit",
                "revenue",
            }
            or broad_business_question
        ):
            plan.append("strategy")

        # Remove duplicates while preserving order
        final_plan = list(dict.fromkeys(plan))

        return {
            "objective": self._determine_objective(intent),
            "plan": final_plan,
            "reasoning": self._explain_plan(
                intent,
                final_plan,
            ),
        }

    # ============================================================
    # OBJECTIVE
    # ============================================================

    def _determine_objective(self, intent) -> str:
        """
        Determine the main business objective.
        """

        metric = intent.metric or "business performance"

        # Multi-period analysis
        if intent.comparison == "previous_periods":
            period_count = getattr(
                intent,
                "period_count",
                None,
            ) or 3

            return (
                f"Compare business performance across the "
                f"previous {period_count} periods, "
                f"identify the direction and largest movement, "
                f"and highlight the appropriate management action."
            )

        # Profit
        if metric == "profit":
            if intent.comparison:
                return (
                    "Compare profitability across the requested "
                    "periods, identify the major drivers of change, "
                    "and recommend management actions."
                )

            return (
                "Analyze business profitability and identify "
                "important performance drivers and actions."
            )

        # Revenue
        if metric == "revenue":
            if intent.comparison:
                return (
                    "Compare revenue performance across periods, "
                    "identify major changes and their drivers, "
                    "and recommend appropriate actions."
                )

            return (
                "Analyze revenue performance and identify "
                "important business growth opportunities."
            )

        # Orders
        if metric == "orders":
            return (
                "Analyze order performance, identify important "
                "changes or drivers, and recommend actions."
            )

        # Customers
        if metric == "customers":
            return (
                "Analyze customer performance and identify "
                "acquisition, retention, or growth opportunities."
            )

        # Units
        if metric == "units_sold":
            return (
                "Analyze unit sales performance and identify "
                "important product or category movements."
            )

        # Discounts
        if metric == "discounts":
            return (
                "Analyze discount activity and determine its "
                "impact on business performance."
            )

        # ROAS
        if metric == "roas":
            return (
                "Analyze marketing return on ad spend and identify "
                "channels requiring budget optimization."
            )

        # CAC
        if metric == "cac":
            return (
                "Analyze customer acquisition cost and identify "
                "opportunities to improve acquisition efficiency."
            )

        # Conversion
        if metric == "conversion_rate":
            return (
                "Analyze marketing conversion performance and "
                "identify opportunities to improve efficiency."
            )

        return (
            "Analyze the requested business question and provide "
            "evidence-based management recommendations."
        )

    # ============================================================
    # PLAN EXPLANATION
    # ============================================================

    def _explain_plan(
        self,
        intent,
        plan: List[str],
    ) -> List[str]:
        """
        Explain why each stage was selected.
        """

        reasons = []

        for stage in plan:

            if stage == "analysis":
                reasons.append(
                    "Data Analysis Agent is required to retrieve "
                    "and quantify the requested business metric."
                )

            elif stage == "root_cause":
                reasons.append(
                    "Root Cause Analysis Agent is required because "
                    "the question involves comparison or performance change."
                )

            elif stage == "marketing":
                reasons.append(
                    "Marketing Analysis Agent is required because "
                    "the question involves marketing efficiency, "
                    "ROAS, CAC, conversion, campaigns, or acquisition."
                )

            elif stage == "cross_domain":
                reasons.append(
                    "Cross-Domain Analysis Agent is required to "
                    "connect independent business evidence streams "
                    "and identify meaningful relationships."
                )

            elif stage == "recommendation":
                reasons.append(
                    "Recommendation Agent is required to convert "
                    "analytical findings into actionable management actions."
                )

            elif stage == "strategy":
                reasons.append(
                    "Strategy Agent is required to prioritize "
                    "important business actions for management."
                )

        return reasons

    # ============================================================
    # PLAN EXECUTION
    # ============================================================

    def execute_plan(
        self,
        plan: Dict[str, Any],
        stage_functions: Dict[str, Callable],
    ) -> Dict[str, Any]:
        """
        Execute the dynamically generated plan.

        stage_functions example:

        {
            "analysis": run_analysis,
            "root_cause": run_root_cause,
            "marketing": run_marketing,
            "cross_domain": run_cross_domain,
            "recommendation": run_recommendation,
            "strategy": run_strategy,
        }
        """

        planned_stages = plan.get(
            "plan",
            [],
        )

        results: Dict[str, Any] = {}

        executed_stages: List[str] = []
        failed_stages: List[str] = []
        skipped_stages: List[str] = []

        for stage in planned_stages:

            function = stage_functions.get(stage)

            if function is None:
                skipped_stages.append(stage)

                results[stage] = {
                    "status": "skipped",
                    "reason": "No execution function registered.",
                }

                continue

            try:

                stage_result = function()

                results[stage] = stage_result

                executed_stages.append(stage)

            except Exception as exc:

                failed_stages.append(stage)

                results[stage] = {
                    "status": "failed",
                    "error": str(exc),
                }

                # Continue executing remaining independent
                # stages instead of stopping the entire workflow.

                continue

        # --------------------------------------------------------
        # Orchestration metadata
        # --------------------------------------------------------

        results["_orchestration"] = {
            "planned_stages": planned_stages,
            "executed_stages": executed_stages,
            "failed_stages": failed_stages,
            "skipped_stages": skipped_stages,
            "objective": plan.get(
                "objective",
                "",
            ),
            "reasoning": plan.get(
                "reasoning",
                [],
            ),
        }

        return results

    # ============================================================
    # EVIDENCE EVALUATION
    # ============================================================

    def evaluate_evidence(
        self,
        intent,
        execution_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Evaluate whether the workflow produced enough evidence
        to answer the business question.
        """

        orchestration = execution_results.get(
            "_orchestration",
            {},
        )

        executed = orchestration.get(
            "executed_stages",
            [],
        )

        failed = orchestration.get(
            "failed_stages",
            [],
        )

        evidence: List[str] = []
        missing: List[str] = []

        # --------------------------------------------------------
        # Business analysis
        # --------------------------------------------------------

        analysis = execution_results.get(
            "analysis",
        )

        if analysis:
            evidence.append(
                "Primary business metric analysis is available."
            )
        else:
            missing.append(
                "Primary business metric analysis."
            )

        # --------------------------------------------------------
        # Root cause
        # --------------------------------------------------------

        root_cause = execution_results.get(
            "root_cause",
        )

        if root_cause:
            evidence.append(
                "Root cause analysis evidence is available."
            )

        # --------------------------------------------------------
        # Marketing
        # --------------------------------------------------------

        marketing = execution_results.get(
            "marketing",
        )

        if marketing:
            evidence.append(
                "Marketing performance evidence is available."
            )

        # --------------------------------------------------------
        # Cross-domain
        # --------------------------------------------------------

        cross_domain = execution_results.get(
            "cross_domain",
        )

        if cross_domain:
            evidence.append(
                "Cross-domain evidence is available."
            )

        # --------------------------------------------------------
        # Recommendations
        # --------------------------------------------------------

        recommendations = execution_results.get(
            "recommendation",
        )

        if recommendations:
            evidence.append(
                "Actionable recommendations are available."
            )

        # --------------------------------------------------------
        # Determine sufficiency
        # --------------------------------------------------------

        sufficient = len(evidence) > 0

        # Root-cause questions need root-cause evidence
        if intent.comparison and (
            intent.comparison != "previous_periods"
        ):
            if not root_cause:
                missing.append(
                    "Root cause evidence for the requested comparison."
                )

        # Marketing questions need marketing evidence
        if intent.metric in {
            "roas",
            "cac",
            "conversion_rate",
        }:
            if not marketing:
                missing.append(
                    "Marketing performance evidence."
                )

        # Multi-period analysis does not require root cause
        # unless the user explicitly asks why.
        if intent.comparison == "previous_periods":
            if analysis:
                sufficient = True

        if missing:
            sufficient = False

        return {
            "sufficient": sufficient,
            "evidence": evidence,
            "missing": missing,
            "executed_stages": executed,
            "failed_stages": failed,
        }

    # ============================================================
    # REPLANNING
    # ============================================================

    def should_replan(
        self,
        evidence: Dict[str, Any],
    ) -> bool:
        """
        Decide whether another analytical stage is required.
        """

        if evidence.get("sufficient"):
            return False

        missing = evidence.get(
            "missing",
            [],
        )

        return len(missing) > 0

    # ============================================================
    # OPTIONAL REPLAN
    # ============================================================

    def create_replan(
        self,
        intent,
        evidence: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create a lightweight follow-up plan when evidence
        evaluation identifies missing information.
        """

        plan = []

        missing_text = " ".join(
            evidence.get(
                "missing",
                [],
            )
        ).lower()

        if (
            "root cause" in missing_text
            and intent.comparison != "previous_periods"
        ):
            plan.append("root_cause")

        if (
            "marketing" in missing_text
            or intent.metric in {
                "roas",
                "cac",
                "conversion_rate",
            }
        ):
            plan.append("marketing")

        if (
            "cross-domain" in missing_text
            or (
                intent.metric in {
                    "profit",
                    "revenue",
                }
                and intent.comparison
            )
        ):
            plan.append("cross_domain")

        if not plan:
            plan.append("analysis")

        plan = list(
            dict.fromkeys(plan)
        )

        return {
            "objective": (
                "Collect additional evidence required "
                "to answer the business question."
            ),
            "plan": plan,
            "reasoning": [
                "Evidence evaluation identified missing analytical evidence.",
                "Additional specialized agents were selected to fill the evidence gap.",
            ],
        }