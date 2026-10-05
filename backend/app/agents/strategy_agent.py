"""
Strategic Strategy Agent

Converts business analysis and root-cause evidence into
data-driven strategic opportunities.

Strategy groups:
    1. Profit Recovery
    2. Profitable Growth
    3. Risk Protection

The agent is designed for CEO / Founder decision support.
"""


def _safe_float(value, default=0.0):
    """Safely convert a value to float."""

    try:
        if value is None:
            return default

        return float(value)

    except (TypeError, ValueError):
        return default


def _build_strategy(
    *,
    category,
    strategy_type,
    priority,
    action,
    reason,
    expected_impact,
    time_horizon,
    owner,
    revenue_change,
    profit_change,
    margin_change,
    return_change,
    discount_change
):
    """Create a standard strategy object."""

    return {
        "category": category,
        "strategy_type": strategy_type,
        "priority": priority,
        "action": action,
        "reason": reason,
        "expected_impact": expected_impact,
        "time_horizon": time_horizon,
        "owner": owner,
        "evidence": {
            "revenue_change": revenue_change,
            "profit_change": profit_change,
            "margin_change_percentage_points": margin_change,
            "return_rate_change_percentage_points": return_change,
            "discount_rate_change_percentage_points": discount_change
        }
    }


def _priority_rank(priority):
    """Convert priority into a sortable value."""

    return {
        "High": 0,
        "Medium": 1,
        "Low": 2
    }.get(priority, 99)


def generate_strategic_strategies(root_cause_analysis):
    """
    Generate strategic strategies from root-cause analysis.

    Output structure:

    {
        "profit_recovery": [],
        "profitable_growth": [],
        "risk_protection": []
    }

    This prevents profitable-growth opportunities from being
    hidden by profit-recovery recommendations.
    """

    if not root_cause_analysis:
        return {
            "profit_recovery": [],
            "profitable_growth": [],
            "risk_protection": []
        }

    categories = root_cause_analysis.get(
        "categories",
        []
    )

    if not categories:
        return {
            "profit_recovery": [],
            "profitable_growth": [],
            "risk_protection": []
        }

    profit_recovery = []
    profitable_growth = []
    risk_protection = []

    for category_data in categories:

        category = category_data.get(
            "category",
            "Unknown"
        )

        # --------------------------------------------------
        # METRICS
        # --------------------------------------------------

        revenue_change = _safe_float(
            category_data.get(
                "revenue_change_percent"
            )
        )

        profit_change = _safe_float(
            category_data.get(
                "profit_change_percent"
            )
        )

        profit_change_amount = _safe_float(
            category_data.get(
                "profit_change"
            )
        )

        margin_change = _safe_float(
            category_data.get(
                "margin_change_percentage_points"
            )
        )

        current_margin = _safe_float(
            category_data.get(
                "current_margin_percent"
            )
        )

        return_change = _safe_float(
            category_data.get(
                "return_rate_change_percentage_points"
            )
        )

        discount_change = _safe_float(
            category_data.get(
                "discount_rate_change_percentage_points"
            )
        )

        # ==================================================
        # 1. PROFIT RECOVERY
        # ==================================================

        if profit_change < 0:

            reasons = []

            if margin_change < 0:
                reasons.append(
                    f"margin declined by "
                    f"{abs(margin_change):.2f} percentage points"
                )

            if return_change > 0:
                reasons.append(
                    f"return rate increased by "
                    f"{return_change:.2f} percentage points"
                )

            if discount_change > 0:
                reasons.append(
                    f"discount rate increased by "
                    f"{discount_change:.2f} percentage points"
                )

            if not reasons:
                reasons.append(
                    f"profit declined by "
                    f"{abs(profit_change):.2f}%"
                )

            profit_recovery.append(
                _build_strategy(
                    category=category,
                    strategy_type="Profit Recovery",
                    priority="High",
                    action=(
                        f"Recover profitability in {category} "
                        f"by addressing the category's "
                        f"main profit-loss drivers."
                    ),
                    reason="; ".join(reasons),
                    expected_impact=(
                        f"Recover part of the "
                        f"₹{abs(profit_change_amount):,.0f} "
                        f"profit decline."
                    ),
                    time_horizon="1-4 weeks",
                    owner="Business / Category Manager",
                    revenue_change=revenue_change,
                    profit_change=profit_change,
                    margin_change=margin_change,
                    return_change=return_change,
                    discount_change=discount_change
                )
            )

        # ==================================================
        # 2. PROFITABLE GROWTH
        # ==================================================

        if (
            revenue_change > 0
            and profit_change > 0
        ):

            profitable_growth.append(
                _build_strategy(
                    category=category,
                    strategy_type="Profitable Growth",
                    priority="High",
                    action=(
                        f"Scale profitable sales in {category} "
                        f"through targeted promotion, "
                        f"strong product visibility and "
                        f"inventory availability."
                    ),
                    reason=(
                        f"Revenue increased by "
                        f"{revenue_change:.2f}% and profit "
                        f"increased by "
                        f"{profit_change:.2f}%."
                    ),
                    expected_impact=(
                        "Increase sales while preserving "
                        "profitable unit economics."
                    ),
                    time_horizon="2-6 weeks",
                    owner="Sales / Marketing Manager",
                    revenue_change=revenue_change,
                    profit_change=profit_change,
                    margin_change=margin_change,
                    return_change=return_change,
                    discount_change=discount_change
                )
            )

        # ==================================================
        # 3. HIGH-MARGIN EXPANSION
        # ==================================================

        if (
            current_margin >= 30
            and profit_change > 0
        ):

            profitable_growth.append(
                _build_strategy(
                    category=category,
                    strategy_type="High-Margin Expansion",
                    priority="Medium",
                    action=(
                        f"Increase visibility and sales volume "
                        f"for high-margin products in "
                        f"{category}."
                    ),
                    reason=(
                        f"Current category margin is "
                        f"{current_margin:.2f}% and profit "
                        f"is growing."
                    ),
                    expected_impact=(
                        "Increase contribution from "
                        "healthy-margin products."
                    ),
                    time_horizon="2-6 weeks",
                    owner="Sales / Category Manager",
                    revenue_change=revenue_change,
                    profit_change=profit_change,
                    margin_change=margin_change,
                    return_change=return_change,
                    discount_change=discount_change
                )
            )

        # ==================================================
        # 4. RETURN REDUCTION
        # ==================================================

        if return_change >= 2:

            risk_protection.append(
                _build_strategy(
                    category=category,
                    strategy_type="Return Reduction",
                    priority=(
                        "High"
                        if return_change >= 5
                        else "Medium"
                    ),
                    action=(
                        f"Investigate and reduce return "
                        f"drivers in {category}."
                    ),
                    reason=(
                        f"Return rate increased by "
                        f"{return_change:.2f} "
                        f"percentage points."
                    ),
                    expected_impact=(
                        "Reduce refund leakage and "
                        "protect realized profit."
                    ),
                    time_horizon="2-4 weeks",
                    owner="Operations / Product Manager",
                    revenue_change=revenue_change,
                    profit_change=profit_change,
                    margin_change=margin_change,
                    return_change=return_change,
                    discount_change=discount_change
                )
            )

        # ==================================================
        # 5. DISCOUNT OPTIMIZATION
        # ==================================================

        if (
            discount_change >= 1
            and margin_change < 0
        ):

            risk_protection.append(
                _build_strategy(
                    category=category,
                    strategy_type="Discount Optimization",
                    priority="High",
                    action=(
                        f"Review discounting in {category} "
                        f"and replace broad discounts "
                        f"with targeted offers."
                    ),
                    reason=(
                        f"Discount rate increased by "
                        f"{discount_change:.2f} percentage points "
                        f"while margin declined by "
                        f"{abs(margin_change):.2f} "
                        f"percentage points."
                    ),
                    expected_impact=(
                        "Protect profit margin while "
                        "maintaining targeted sales volume."
                    ),
                    time_horizon="1-2 weeks",
                    owner="Pricing / Marketing Manager",
                    revenue_change=revenue_change,
                    profit_change=profit_change,
                    margin_change=margin_change,
                    return_change=return_change,
                    discount_change=discount_change
                )
            )

        # ==================================================
        # 6. MARGIN PROTECTION
        # ==================================================

        if (
            revenue_change > 0
            and profit_change < 0
            and margin_change < 0
        ):

            risk_protection.append(
                _build_strategy(
                    category=category,
                    strategy_type="Margin Protection",
                    priority="High",
                    action=(
                        f"Protect margins in {category} "
                        f"before aggressively scaling sales."
                    ),
                    reason=(
                        f"Revenue increased by "
                        f"{revenue_change:.2f}% but profit "
                        f"declined by "
                        f"{abs(profit_change):.2f}%, "
                        f"while margin declined by "
                        f"{abs(margin_change):.2f} "
                        f"percentage points."
                    ),
                    expected_impact=(
                        "Convert revenue growth into "
                        "profitable growth."
                    ),
                    time_horizon="2-6 weeks",
                    owner="Pricing / Finance Manager",
                    revenue_change=revenue_change,
                    profit_change=profit_change,
                    margin_change=margin_change,
                    return_change=return_change,
                    discount_change=discount_change
                )
            )

    # ======================================================
    # REMOVE DUPLICATES
    # ======================================================

    def remove_duplicates(strategies):

        unique = []
        seen = set()

        for strategy in strategies:

            key = (
                strategy.get(
                    "category",
                    ""
                ).lower(),

                strategy.get(
                    "strategy_type",
                    ""
                ).lower()
            )

            if key in seen:
                continue

            seen.add(key)
            unique.append(strategy)

        return unique

    profit_recovery = remove_duplicates(
        profit_recovery
    )

    profitable_growth = remove_duplicates(
        profitable_growth
    )

    risk_protection = remove_duplicates(
        risk_protection
    )

    # ======================================================
    # SORTING
    # ======================================================

    # Profit recovery:
    # Largest absolute ₹ profit loss first.

    profit_recovery.sort(
        key=lambda x: abs(
            _safe_float(
                next(
                    (
                        c.get("profit_change", 0)
                        for c in categories
                        if c.get("category")
                        == x.get("category")
                    ),
                    0
                )
            )
        ),
        reverse=True
    )

    # Profitable growth:
    # Profit growth first, then revenue growth.

    profitable_growth.sort(
        key=lambda x: (
            _safe_float(
                x.get(
                    "evidence",
                    {}
                ).get(
                    "profit_change"
                )
            ),
            _safe_float(
                x.get(
                    "evidence",
                    {}
                ).get(
                    "revenue_change"
                )
            )
        ),
        reverse=True
    )

    # Risk protection:
    # High priority first,
    # then largest return / discount pressure.

    risk_protection.sort(
        key=lambda x: (
            _priority_rank(
                x.get("priority")
            ),
            max(
                abs(
                    _safe_float(
                        x.get(
                            "evidence",
                            {}
                        ).get(
                            "return_rate_change_percentage_points"
                        )
                    )
                ),
                abs(
                    _safe_float(
                        x.get(
                            "evidence",
                            {}
                        ).get(
                            "discount_rate_change_percentage_points"
                        )
                    )
                )
            )
        )
    )

    # ======================================================
    # LIMIT RESULTS
    # ======================================================

    return {
        "profit_recovery": profit_recovery[:3],
        "profitable_growth": profitable_growth[:3],
        "risk_protection": risk_protection[:3]
    }


def generate_strategy_summary(strategy_groups):
    """
    Generate a short CEO-oriented strategic summary.
    """

    if not strategy_groups:
        return (
            "No major strategic opportunity was identified "
            "from the available comparison data."
        )

    areas = []

    if strategy_groups.get(
        "profit_recovery"
    ):
        areas.append(
            "Profit Recovery"
        )

    if strategy_groups.get(
        "profitable_growth"
    ):
        areas.append(
            "Profitable Growth"
        )

    if strategy_groups.get(
        "risk_protection"
    ):
        areas.append(
            "Risk Protection"
        )

    if not areas:
        return (
            "No major strategic opportunity was identified "
            "from the available comparison data."
        )

    return (
        "Strategic focus areas: "
        + ", ".join(areas)
        + "."
    )