# ============================================================
# PRODUCT RECOMMENDATIONS
# ============================================================

def generate_recommendations(
    product,
    analysis
):

    recommendations = []

    margin = float(
        product.get(
            "profit_margin_percent",
            0
        )
    )

    profit = float(
        product.get(
            "profit",
            0
        )
    )

    discount = float(
        product.get(
            "discount",
            0
        )
    )

    cost = float(
        product.get(
            "cost",
            0
        )
    )

    revenue = float(
        product.get(
            "revenue",
            0
        )
    )

    # --------------------------------------------------------
    # NEGATIVE MARGIN
    # --------------------------------------------------------

    if margin < 0:

        recommendations.append({

            "action":
                "Review product pricing immediately",

            "priority":
                "Critical",

            "reason": (
                f"The product has a negative "
                f"margin of {margin:.2f}% "
                f"and generated a loss of "
                f"₹{abs(profit):,.2f}."
            ),

            "expected_impact":
                "Restore the product to positive profitability.",

            "time_horizon":
                "Immediate",

            "owner":
                "Business / Pricing Manager"
        })

    # --------------------------------------------------------
    # DISCOUNT
    # --------------------------------------------------------

    if discount > 0:

        recommendations.append({

            "action":
                "Reduce or restructure discounts",

            "priority":
                "High",

            "reason": (
                f"Discounts of "
                f"₹{discount:,.2f} "
                "may be reducing realized profitability."
            ),

            "expected_impact":
                "Improve realized margin.",

            "time_horizon":
                "1-2 weeks",

            "owner":
                "Marketing / Pricing Manager"
        })

    # --------------------------------------------------------
    # COST > REVENUE
    # --------------------------------------------------------

    if cost > revenue:

        recommendations.append({

            "action":
                "Review supplier and product cost",

            "priority":
                "High",

            "reason": (
                f"Product cost of "
                f"₹{cost:,.2f} "
                "exceeds generated revenue."
            ),

            "expected_impact":
                "Lower product cost and improve profitability.",

            "time_horizon":
                "2-4 weeks",

            "owner":
                "Procurement Manager"
        })

    # --------------------------------------------------------
    # DEFAULT
    # --------------------------------------------------------

    if not recommendations:

        recommendations.append({

            "action":
                "Continue monitoring product performance",

            "priority":
                "Medium",

            "reason":
                "The product is currently profitable.",

            "expected_impact":
                "Maintain healthy profitability.",

            "time_horizon":
                "Monthly",

            "owner":
                "Business Manager"
        })

    return {

        "product":
            product.get("product_name"),

        "decision": (
            "Immediate intervention required"
            if margin < 0
            else "Continue monitoring"
        ),

        "recommendations":
            recommendations
    }


# ============================================================
# GENERAL QUERY RECOMMENDATIONS
# ============================================================

def generate_query_recommendations(
    intent,
    analysis
):

    recommendations = []

    # --------------------------------------------------------
    # DECLINE ANALYSIS
    # --------------------------------------------------------

    if "decline" in intent.intent:

        change = analysis.get(
            "change_percent",
            0
        )

        if change < 0:

            recommendations.append({

                "action":
                    "Investigate the drivers of the decline",

                "priority":
                    "High",

                "reason": (
                    f"{intent.metric.title()} "
                    f"decreased by "
                    f"{abs(change):.2f}% "
                    "compared with the previous period."
                ),

                "time_horizon":
                    "Immediate",

                "owner":
                    "Business / Strategy Manager"
            })

    # --------------------------------------------------------
    # DIMENSION ANALYSIS
    # --------------------------------------------------------

    elif intent.dimension:

        top = analysis.get(
            "top_dimension"
        )

        if top:

            recommendations.append({

                "action": (
                    f"Review {intent.dimension} "
                    "performance and identify "
                    "growth opportunities"
                ),

                "priority":
                    "Medium",

                "reason": (
                    f"{top['dimension']} is the leading "
                    f"{intent.dimension} for the selected metric."
                ),

                "time_horizon":
                    "1-2 weeks",

                "owner":
                    "Business Analyst"
            })

    # --------------------------------------------------------
    # DEFAULT
    # --------------------------------------------------------

    if not recommendations:

        recommendations.append({

            "action":
                "Continue monitoring the selected KPI",

            "priority":
                "Medium",

            "reason":
                "No significant negative movement was detected.",

            "time_horizon":
                "Monthly",

            "owner":
                "Business Manager"
        })

    return recommendations


# ============================================================
# ROOT CAUSE RECOMMENDATIONS
# ============================================================

# ============================================================
# ROOT CAUSE RECOMMENDATION ENGINE
# ============================================================

def generate_root_cause_recommendations(root_cause_analysis):
    """
    Generate a concise CEO-focused Top 3 recommendation list.

    Ranking is primarily based on absolute profit impact.
    Margin, return and discount changes are used as
    supporting evidence.

    Maximum 3 recommendations are returned.
    Duplicate category actions are avoided.
    """

    recommendations = []

    declining_categories = root_cause_analysis.get(
        "profit_declining_categories",
        []
    )

    # ========================================================
    # 1. CATEGORY PROFIT DECLINE
    # ========================================================

    for category in declining_categories:

        category_name = category.get(
            "category",
            "Unknown"
        )

        # Absolute profit change in ₹
        profit_change = float(
            category.get(
                "profit_change",
                0
            ) or 0
        )

        # Profit change percentage
        profit_change_percent = float(
            category.get(
                "profit_change_percent",
                0
            ) or 0
        )

        # Margin change in percentage points
        margin_change = float(
            category.get(
                "margin_change_percentage_points",
                0
            ) or 0
        )

        # Return-rate change in percentage points
        return_change = float(
            category.get(
                "return_rate_change_percentage_points",
                0
            ) or 0
        )

        # Discount-rate change in percentage points
        discount_change = float(
            category.get(
                "discount_rate_change_percentage_points",
                0
            ) or 0
        )

        # ----------------------------------------------------
        # Only categories with actual profit decline
        # ----------------------------------------------------

        if profit_change >= 0:
            continue

        reasons = []

        # ----------------------------------------------------
        # Margin evidence
        # ----------------------------------------------------

        if margin_change < 0:

            reasons.append(
                f"profit margin declined by "
                f"{abs(margin_change):.2f} percentage points"
            )

        # ----------------------------------------------------
        # Return evidence
        # ----------------------------------------------------

        if return_change > 0:

            reasons.append(
                f"return rate increased by "
                f"{return_change:.2f} percentage points"
            )

        # ----------------------------------------------------
        # Discount evidence
        # ----------------------------------------------------

        if discount_change > 0:

            reasons.append(
                f"discount rate increased by "
                f"{discount_change:.2f} percentage points"
            )

        # ----------------------------------------------------
        # Fallback evidence
        # ----------------------------------------------------

        if not reasons:

            reasons.append(
                f"profit declined by "
                f"{abs(profit_change_percent):.2f}%"
            )

        # ----------------------------------------------------
        # Create recommendation
        # ----------------------------------------------------

        recommendations.append({

            "action":
                f"Address {category_name} profitability decline",

            "priority":
                "High",

            "reason":
                "; ".join(reasons),

            "expected_impact":
                f"Recover approximately "
                f"₹{abs(profit_change):,.0f} "
                f"in lost category profit.",

            "time_horizon":
                "1-2 weeks",

            "owner":
                "Business / Pricing Manager",

            # Internal ranking field
            "_profit_impact":
                profit_change
        })

    # ========================================================
    # 2. RETURN PRESSURE
    # ========================================================

    highest_return = root_cause_analysis.get(
        "highest_return_pressure"
    )

    if highest_return:

        category_name = highest_return.get(
            "category",
            "Unknown"
        )

        return_change = float(
            highest_return.get(
                "return_rate_change_percentage_points",
                0
            ) or 0
        )

        category_profit_change = float(
            highest_return.get(
                "profit_change",
                0
            ) or 0
        )

        # Only consider meaningful return pressure
        if return_change >= 2:

            # Check whether this category already has
            # a profitability recommendation.
            already_covered = any(

                recommendation["action"]
                .lower()
                .find(category_name.lower()) >= 0

                for recommendation in recommendations
            )

            if not already_covered:

                recommendations.append({

                    "action":
                        f"Investigate return drivers in "
                        f"{category_name}",

                    "priority":
                        "High"
                        if return_change >= 5
                        else "Medium",

                    "reason":
                        f"return rate increased by "
                        f"{return_change:.2f} percentage points",

                    "expected_impact":
                        "Reduce refund leakage and "
                        "protect realized profit.",

                    "time_horizon":
                        "2-4 weeks",

                    "owner":
                        "Operations / Product Manager",

                    # Use the same ranking field
                    "_profit_impact":
                        category_profit_change
                })

    # ========================================================
    # 3. DISCOUNT PRESSURE
    # ========================================================

    highest_discount = root_cause_analysis.get(
        "highest_discount_pressure"
    )

    if highest_discount:

        category_name = highest_discount.get(
            "category",
            "Unknown"
        )

        discount_change = float(
            highest_discount.get(
                "discount_rate_change_percentage_points",
                0
            ) or 0
        )

        category_profit_change = float(
            highest_discount.get(
                "profit_change",
                0
            ) or 0
        )

        # Only consider meaningful discount pressure
        if discount_change >= 1:

            # Check whether this category already has
            # a profitability recommendation.
            already_covered = any(

                recommendation["action"]
                .lower()
                .find(category_name.lower()) >= 0

                for recommendation in recommendations
            )

            if not already_covered:

                recommendations.append({

                    "action":
                        f"Review discount strategy for "
                        f"{category_name}",

                    "priority":
                        "High",

                    "reason":
                        f"discount rate increased by "
                        f"{discount_change:.2f} percentage points",

                    "expected_impact":
                        "Protect profit margin from "
                        "excessive discounting.",

                    "time_horizon":
                        "1-2 weeks",

                    "owner":
                        "Pricing / Marketing Manager",

                    # Same ranking field
                    "_profit_impact":
                        category_profit_change
                })

    # ========================================================
    # 4. SORT BY FINANCIAL IMPACT
    # ========================================================

    # Profit decline values are negative.
    # Example:
    #
    # Sports       -151802
    # Home Kitchen -138118
    # Fashion       -78405
    #
    # Ascending order therefore places the
    # largest profit loss first.

    recommendations.sort(
        key=lambda x: x.get(
            "_profit_impact",
            0
        )
    )

    # ========================================================
    # 5. TOP 3 ONLY
    # ========================================================

    recommendations = recommendations[:3]

    # ========================================================
    # 6. REMOVE INTERNAL FIELD
    # ========================================================

    for recommendation in recommendations:

        recommendation.pop(
            "_profit_impact",
            None
        )

    return recommendations