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

# ============================================================
# GENERAL QUERY RECOMMENDATIONS
# ============================================================


def generate_query_recommendations(
    intent,
    analysis
):
    """
    Generate recommendations for general business
    and marketing questions.

    Supports:

    - KPI analysis
    - Decline analysis
    - Dimension analysis
    - ROAS
    - CAC
    - Conversion rate
    - Marketing channel analysis
    """

    recommendations = []

    analysis = analysis or {}

    metric = getattr(
        intent,
        "metric",
        None
    )

    intent_name = getattr(
        intent,
        "intent",
        ""
    )

    dimension = getattr(
        intent,
        "dimension",
        None
    )

    # ========================================================
    # MARKETING ANALYSIS
    # ========================================================

    marketing_metrics = {
        "roas",
        "cac",
        "conversion_rate",
    }

    marketing_intents = {
        "marketing_analysis",
        "marketing_channel_analysis",
        "marketing_channel_comparison",
    }

    if (
        metric in marketing_metrics
        or intent_name in marketing_intents
    ):

        # ----------------------------------------------------
        # Extract marketing analysis
        # ----------------------------------------------------

        channels = (
            analysis.get(
                "channels",
                []
            )
            or []
        )

        # Some callers may wrap the analysis
        # inside another result object.

        if not channels:

            nested_analysis = (
                analysis.get(
                    "analysis",
                    {}
                )
                or {}
            )

            if isinstance(
                nested_analysis,
                dict
            ):

                channels = (
                    nested_analysis.get(
                        "channels",
                        []
                    )
                    or []
                )

        # ----------------------------------------------------
        # ROAS ANALYSIS
        # ----------------------------------------------------

        if metric == "roas":

            # Find the lowest ROAS channel.

            valid_channels = [
                channel
                for channel in channels
                if isinstance(
                    channel,
                    dict
                )
            ]

            if valid_channels:

                lowest_roas_channel = min(
                    valid_channels,
                    key=lambda x: float(
                        x.get(
                            "roas",
                            0
                        ) or 0
                    )
                )

                highest_roas_channel = max(
                    valid_channels,
                    key=lambda x: float(
                        x.get(
                            "roas",
                            0
                        ) or 0
                    )
                )

                lowest_roas = float(
                    lowest_roas_channel.get(
                        "roas",
                        0
                    ) or 0
                )

                highest_roas = float(
                    highest_roas_channel.get(
                        "roas",
                        0
                    ) or 0
                )

                lowest_channel_name = (
                    lowest_roas_channel.get(
                        "channel",
                        "Unknown"
                    )
                )

                highest_channel_name = (
                    highest_roas_channel.get(
                        "channel",
                        "Unknown"
                    )
                )

                # ------------------------------------------------
                # LOW ROAS CHANNEL
                # ------------------------------------------------

                if lowest_roas < 3:

                    recommendations.append({

                        "action":
                            (
                                f"Review and optimize "
                                f"{lowest_channel_name} "
                                f"budget allocation"
                            ),

                        "priority":
                            "High",

                        "reason":
                            (
                                f"{lowest_channel_name} "
                                f"generated only "
                                f"{lowest_roas:.2f}x ROAS."
                            ),

                        "expected_impact":
                            (
                                "Improve marketing efficiency "
                                "by reducing spend leakage "
                                "from underperforming channels."
                            ),

                        "time_horizon":
                            "1-2 weeks",

                        "owner":
                            "Marketing Manager",
                    })

                # ------------------------------------------------
                # HIGH ROAS CHANNEL
                # ------------------------------------------------

                if (
                    highest_roas >= 4
                    and highest_channel_name
                    != lowest_channel_name
                ):

                    recommendations.append({

                        "action":
                            (
                                f"Increase controlled investment "
                                f"in {highest_channel_name}"
                            ),

                        "priority":
                            "Medium",

                        "reason":
                            (
                                f"{highest_channel_name} "
                                f"generated the strongest ROAS "
                                f"at {highest_roas:.2f}x."
                            ),

                        "expected_impact":
                            (
                                "Scale efficient customer "
                                "acquisition while maintaining "
                                "marketing efficiency."
                            ),

                        "time_horizon":
                            "2-4 weeks",

                        "owner":
                            "Marketing Manager",
                    })

        # ----------------------------------------------------
        # CAC ANALYSIS
        # ----------------------------------------------------

        elif metric == "cac":

            valid_channels = [
                channel
                for channel in channels
                if isinstance(
                    channel,
                    dict
                )
            ]

            if valid_channels:

                highest_cac_channel = max(
                    valid_channels,
                    key=lambda x: float(
                        x.get(
                            "cac",
                            0
                        ) or 0
                    )
                )

                lowest_cac_channel = min(
                    [
                        channel
                        for channel in valid_channels
                        if float(
                            channel.get(
                                "cac",
                                0
                            ) or 0
                        ) > 0
                    ],
                    key=lambda x: float(
                        x.get(
                            "cac",
                            0
                        ) or 0
                    ),
                    default=None
                )

                highest_cac = float(
                    highest_cac_channel.get(
                        "cac",
                        0
                    ) or 0
                )

                highest_cac_name = (
                    highest_cac_channel.get(
                        "channel",
                        "Unknown"
                    )
                )

                if highest_cac > 50:

                    recommendations.append({

                        "action":
                            (
                                f"Reduce acquisition cost "
                                f"in {highest_cac_name}"
                            ),

                        "priority":
                            "High",

                        "reason":
                            (
                                f"{highest_cac_name} has CAC "
                                f"of ₹{highest_cac:,.2f}."
                            ),

                        "expected_impact":
                            (
                                "Improve customer acquisition "
                                "efficiency and reduce marketing "
                                "cost per new customer."
                            ),

                        "time_horizon":
                            "1-2 weeks",

                        "owner":
                            "Marketing Manager",
                    })

                if lowest_cac_channel:

                    lowest_cac = float(
                        lowest_cac_channel.get(
                            "cac",
                            0
                        ) or 0
                    )

                    lowest_cac_name = (
                        lowest_cac_channel.get(
                            "channel",
                            "Unknown"
                        )
                    )

                    recommendations.append({

                        "action":
                            (
                                f"Scale efficient acquisition "
                                f"through {lowest_cac_name}"
                            ),

                        "priority":
                            "Medium",

                        "reason":
                            (
                                f"{lowest_cac_name} has the "
                                f"lowest observed CAC at "
                                f"₹{lowest_cac:,.2f}."
                            ),

                        "expected_impact":
                            (
                                "Acquire additional customers "
                                "through a relatively efficient "
                                "acquisition channel."
                            ),

                        "time_horizon":
                            "2-4 weeks",

                        "owner":
                            "Marketing Manager",
                    })

        # ----------------------------------------------------
        # CONVERSION RATE ANALYSIS
        # ----------------------------------------------------

        elif metric == "conversion_rate":

            valid_channels = [
                channel
                for channel in channels
                if isinstance(
                    channel,
                    dict
                )
            ]

            if valid_channels:

                lowest_conversion_channel = min(
                    valid_channels,
                    key=lambda x: float(
                        x.get(
                            "conversion_rate",
                            0
                        ) or 0
                    )
                )

                highest_conversion_channel = max(
                    valid_channels,
                    key=lambda x: float(
                        x.get(
                            "conversion_rate",
                            0
                        ) or 0
                    )
                )

                lowest_conversion = float(
                    lowest_conversion_channel.get(
                        "conversion_rate",
                        0
                    ) or 0
                )

                highest_conversion = float(
                    highest_conversion_channel.get(
                        "conversion_rate",
                        0
                    ) or 0
                )

                lowest_conversion_name = (
                    lowest_conversion_channel.get(
                        "channel",
                        "Unknown"
                    )
                )

                highest_conversion_name = (
                    highest_conversion_channel.get(
                        "channel",
                        "Unknown"
                    )
                )

                if lowest_conversion < 2:

                    recommendations.append({

                        "action":
                            (
                                f"Improve conversion "
                                f"performance in "
                                f"{lowest_conversion_name}"
                            ),

                        "priority":
                            "High",

                        "reason":
                            (
                                f"{lowest_conversion_name} "
                                f"has conversion rate of "
                                f"{lowest_conversion:.2f}%."
                            ),

                        "expected_impact":
                            (
                                "Increase customer conversion "
                                "from existing traffic."
                            ),

                        "time_horizon":
                            "2-4 weeks",

                        "owner":
                            "Marketing / CRO Manager",
                    })

                if (
                    highest_conversion
                    >= 3
                    and highest_conversion_name
                    != lowest_conversion_name
                ):

                    recommendations.append({

                        "action":
                            (
                                f"Scale traffic to "
                                f"{highest_conversion_name}"
                            ),

                        "priority":
                            "Medium",

                        "reason":
                            (
                                f"{highest_conversion_name} "
                                f"has the strongest conversion "
                                f"rate at "
                                f"{highest_conversion:.2f}%."
                            ),

                        "expected_impact":
                            (
                                "Generate more customers from "
                                "efficient converting traffic."
                            ),

                        "time_horizon":
                            "2-4 weeks",

                        "owner":
                            "Marketing Manager",
                    })

    # ========================================================
    # DECLINE ANALYSIS
    # ========================================================

    if not recommendations and (
        "decline" in intent_name
    ):

        change = float(
            analysis.get(
                "change_percent",
                0
            ) or 0
        )

        if change < 0:

            recommendations.append({

                "action":
                    "Investigate the drivers of the decline",

                "priority":
                    "High",

                "reason":
                    (
                        f"{str(metric).title()} "
                        f"decreased by "
                        f"{abs(change):.2f}% "
                        "compared with the previous period."
                    ),

                "time_horizon":
                    "Immediate",

                "owner":
                    "Business / Strategy Manager",
            })

    # ========================================================
    # DIMENSION ANALYSIS
    # ========================================================

    if not recommendations and dimension:

        top = analysis.get(
            "top_dimension"
        )

        if top:

            recommendations.append({

                "action":
                    (
                        f"Review {dimension} "
                        "performance and identify "
                        "growth opportunities"
                    ),

                "priority":
                    "Medium",

                "reason":
                    (
                        f"{top.get('dimension', 'Unknown')} "
                        f"is the leading {dimension} "
                        "for the selected metric."
                    ),

                "time_horizon":
                    "1-2 weeks",

                "owner":
                    "Business Analyst",
            })

    # ========================================================
    # DEFAULT
    # ========================================================

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
                "Business Manager",
        })

    # ========================================================
    # TOP 3
    # ========================================================

    return recommendations[:3]
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