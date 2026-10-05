from typing import Any, Dict, List


def analyze_cross_domain(
    root_cause: Dict[str, Any],
    marketing: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Combine business root-cause analysis with
    marketing intelligence.

    Important:
    This agent identifies relationships and signals.
    It does not claim causation unless the available
    data directly supports it.
    """

    cross_domain_insights: List[Dict[str, Any]] = []

    # ---------------------------------------------------------
    # ROOT CAUSE DATA
    # ---------------------------------------------------------

    largest_profit_decline = (
        root_cause.get(
            "largest_profit_decline"
        )
        if root_cause
        else None
    )

    highest_return_pressure = (
        root_cause.get(
            "highest_return_pressure"
        )
        if root_cause
        else None
    )

    lowest_margin_category = (
        root_cause.get(
            "lowest_margin_category"
        )
        if root_cause
        else None
    )

    # ---------------------------------------------------------
    # MARKETING DATA
    # ---------------------------------------------------------

    marketing_analysis = (
        marketing.get(
            "analysis",
            {}
        )
        if marketing
        else {}
    )

    top_roas_channel = (
        marketing_analysis.get(
            "top_roas_channel"
        )
    )

    lowest_roas_channel = (
        marketing_analysis.get(
            "lowest_roas_channel"
        )
    )

    highest_spend_channel = (
        marketing_analysis.get(
            "highest_spend_channel"
        )
    )

    # ---------------------------------------------------------
    # 1. PROFIT PRESSURE
    # ---------------------------------------------------------

    if largest_profit_decline:

        category = largest_profit_decline.get(
            "category",
            "Unknown"
        )

        profit_change = float(
            largest_profit_decline.get(
                "profit_change",
                0
            ) or 0
        )

        profit_change_percent = float(
            largest_profit_decline.get(
                "profit_change_percent",
                0
            ) or 0
        )

        revenue_change_percent = float(
            largest_profit_decline.get(
                "revenue_change_percent",
                0
            ) or 0
        )

        cross_domain_insights.append({
            "type": "profit_pressure",

            "title":
                f"{category} is the largest profit pressure",

            "category":
                category,

            "message": (
                f"{category} profit declined by "
                f"{abs(profit_change_percent):.2f}% "
                f"and revenue declined by "
                f"{abs(revenue_change_percent):.2f}%."
            ),

            "evidence": {
                "profit_change":
                    profit_change,

                "profit_change_percent":
                    profit_change_percent,

                "revenue_change_percent":
                    revenue_change_percent
            }
        })

    # ---------------------------------------------------------
    # 2. RETURN PRESSURE
    # ---------------------------------------------------------

    if highest_return_pressure:

        category = highest_return_pressure.get(
            "category",
            "Unknown"
        )

        return_change = float(
            highest_return_pressure.get(
                "return_rate_change_percentage_points",
                0
            ) or 0
        )

        if return_change > 0:

            cross_domain_insights.append({
                "type":
                    "return_pressure",

                "title":
                    f"Return pressure increased in {category}",

                "category":
                    category,

                "message": (
                    f"Return rate increased by "
                    f"{return_change:.2f} "
                    "percentage points."
                ),

                "evidence": {
                    "return_rate_change_percentage_points":
                        return_change
                }
            })

    # ---------------------------------------------------------
    # 3. LOW MARGIN
    # ---------------------------------------------------------

    if lowest_margin_category:

        category = lowest_margin_category.get(
            "category",
            "Unknown"
        )

        margin = float(
            lowest_margin_category.get(
                "current_margin_percent",
                0
            ) or 0
        )

        cross_domain_insights.append({
            "type":
                "margin_pressure",

            "title":
                f"{category} has the lowest current margin",

            "category":
                category,

            "message": (
                f"Current category margin is "
                f"{margin:.2f}%."
            ),

            "evidence": {
                "current_margin_percent":
                    margin
            }
        })

    # ---------------------------------------------------------
    # 4. MARKETING EFFICIENCY
    # ---------------------------------------------------------

    if lowest_roas_channel:

        channel = lowest_roas_channel.get(
            "channel",
            "Unknown"
        )

        roas = float(
            lowest_roas_channel.get(
                "roas",
                0
            ) or 0
        )

        spend = float(
            lowest_roas_channel.get(
                "spend",
                0
            ) or 0
        )

        cross_domain_insights.append({
            "type":
                "marketing_efficiency",

            "title":
                f"{channel} has the lowest marketing ROAS",

            "channel":
                channel,

            "message": (
                f"{channel} generated "
                f"{roas:.2f}x ROAS "
                f"with ₹{spend:,.0f} spend."
            ),

            "evidence": {
                "roas":
                    roas,

                "spend":
                    spend
            }
        })

    # ---------------------------------------------------------
    # 5. MARKETING SPEND CONCENTRATION
    # ---------------------------------------------------------

    if highest_spend_channel:

        channel = highest_spend_channel.get(
            "channel",
            "Unknown"
        )

        spend = float(
            highest_spend_channel.get(
                "spend",
                0
            ) or 0
        )

        roas = float(
            highest_spend_channel.get(
                "roas",
                0
            ) or 0
        )

        cross_domain_insights.append({
            "type":
                "marketing_spend",

            "title":
                f"{channel} has the highest marketing spend",

            "channel":
                channel,

            "message": (
                f"{channel} accounts for "
                f"₹{spend:,.0f} of marketing spend "
                f"with ROAS of {roas:.2f}x."
            ),

            "evidence": {
                "spend":
                    spend,

                "roas":
                    roas
            }
        })

    # ---------------------------------------------------------
    # 6. HIGH-ROAS CHANNEL
    # ---------------------------------------------------------

    if top_roas_channel:

        channel = top_roas_channel.get(
            "channel",
            "Unknown"
        )

        roas = float(
            top_roas_channel.get(
                "roas",
                0
            ) or 0
        )

        cross_domain_insights.append({
            "type":
                "marketing_opportunity",

            "title":
                f"{channel} has the highest marketing ROAS",

            "channel":
                channel,

            "message": (
                f"{channel} generated "
                f"{roas:.2f}x ROAS."
            ),

            "evidence": {
                "roas":
                    roas
            }
        })

    # ---------------------------------------------------------
    # 7. CROSS-DOMAIN INTERPRETATION
    # ---------------------------------------------------------

    cross_domain_summary = []

    if largest_profit_decline:

        category = largest_profit_decline.get(
            "category",
            "Unknown"
        )

        cross_domain_summary.append(
            f"{category} is the largest identified "
            "category-level profit pressure."
        )

    if lowest_roas_channel:

        channel = lowest_roas_channel.get(
            "channel",
            "Unknown"
        )

        cross_domain_summary.append(
            f"{channel} is the lowest-ROAS marketing "
            "channel for the selected period."
        )

    # ---------------------------------------------------------
    # IMPORTANT CAUSATION LIMITATION
    # ---------------------------------------------------------

    causation_note = (
        "Marketing performance and category profitability "
        "are analyzed as separate evidence streams. "
        "The current dataset does not directly establish "
        "that a specific marketing channel caused a "
        "specific category profit change."
    )

    return {
        "insights":
            cross_domain_insights,

        "summary":
            cross_domain_summary,

        "causation_note":
            causation_note
    }


def generate_cross_domain_recommendations(
    cross_domain_analysis: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Generate concise recommendations from
    cross-domain evidence.
    """

    recommendations = []

    insights = cross_domain_analysis.get(
        "insights",
        []
    )

    # ---------------------------------------------------------
    # PROFIT PRESSURE
    # ---------------------------------------------------------

    for insight in insights:

        if insight.get("type") == "profit_pressure":

            category = insight.get(
                "category",
                "Unknown"
            )

            recommendations.append({
                "action":
                    f"Investigate {category} profit decline",

                "priority":
                    "High",

                "reason":
                    insight.get(
                        "message",
                        ""
                    ),

                "expected_impact":
                    "Identify category-level drivers "
                    "of profit deterioration.",

                "time_horizon":
                    "1-2 weeks",

                "owner":
                    "Business / Category Manager"
            })

            break

    # ---------------------------------------------------------
    # RETURN PRESSURE
    # ---------------------------------------------------------

    for insight in insights:

        if insight.get("type") == "return_pressure":

            category = insight.get(
                "category",
                "Unknown"
            )

            recommendations.append({
                "action":
                    f"Investigate return drivers in {category}",

                "priority":
                    "High",

                "reason":
                    insight.get(
                        "message",
                        ""
                    ),

                "expected_impact":
                    "Reduce refund leakage and "
                    "protect realized profit.",

                "time_horizon":
                    "2-4 weeks",

                "owner":
                    "Operations / Product Manager"
            })

            break

    # ---------------------------------------------------------
    # MARKETING EFFICIENCY
    # ---------------------------------------------------------

    for insight in insights:

        if insight.get(
            "type"
        ) == "marketing_efficiency":

            channel = insight.get(
                "channel",
                "Unknown"
            )

            recommendations.append({
                "action":
                    f"Review {channel} marketing efficiency",

                "priority":
                    "Medium",

                "reason":
                    insight.get(
                        "message",
                        ""
                    ),

                "expected_impact":
                    "Improve marketing efficiency "
                    "and customer acquisition economics.",

                "time_horizon":
                    "1-2 weeks",

                "owner":
                    "Marketing Manager"
            })

            break

    # ---------------------------------------------------------
    # MARKETING OPPORTUNITY
    # ---------------------------------------------------------

    for insight in insights:

        if insight.get(
            "type"
        ) == "marketing_opportunity":

            channel = insight.get(
                "channel",
                "Unknown"
            )

            recommendations.append({
                "action":
                    f"Evaluate controlled growth in {channel}",

                "priority":
                    "Medium",

                "reason":
                    insight.get(
                        "message",
                        ""
                    ),

                "expected_impact":
                    "Test additional customer acquisition "
                    "while monitoring efficiency.",

                "time_horizon":
                    "2-4 weeks",

                "owner":
                    "Marketing Manager"
            })

            break

    return recommendations[:4]