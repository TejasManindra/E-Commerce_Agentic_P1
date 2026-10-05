def generate_product_insights(products):
    """
    Generate business insights from product performance data.
    """

    if not products:
        return {
            "insights": [],
            "recommendations": []
        }

    insights = []
    recommendations = []

    # ---------------------------------------------------------
    # Find important products
    # ---------------------------------------------------------

    highest_revenue = max(
        products,
        key=lambda x: x["revenue"]
    )

    highest_profit = max(
        products,
        key=lambda x: x["profit"]
    )

    highest_margin = max(
        products,
        key=lambda x: x["profit_margin_percent"]
    )

    lowest_margin = min(
        products,
        key=lambda x: x["profit_margin_percent"]
    )

    # ---------------------------------------------------------
    # Count product classifications
    # ---------------------------------------------------------

    star_products = [
        p for p in products
        if p["performance_classification"] == "Star Product"
    ]

    revenue_traps = [
        p for p in products
        if p["performance_classification"] == "Revenue Trap"
    ]

    growth_opportunities = [
        p for p in products
        if p["performance_classification"] == "Growth Opportunity"
    ]

    optimization_candidates = [
        p for p in products
        if p["performance_classification"] == "Optimization Candidate"
    ]

    # ---------------------------------------------------------
    # Insight 1 — Revenue leader
    # ---------------------------------------------------------

    insights.append({
        "type": "positive",
        "title": "Top Revenue Product",
        "product": highest_revenue["product_name"],
        "insight": (
            f'{highest_revenue["product_name"]} generated '
            f'₹{highest_revenue["revenue"]:,.2f} in revenue '
            f'and contributed '
            f'{highest_revenue["revenue_share_percent"]:.2f}% '
            f'of product revenue.'
        ),
        "business_impact": (
            "This product is an important contributor to overall sales."
        )
    })

    # ---------------------------------------------------------
    # Insight 2 — Profit leader
    # ---------------------------------------------------------

    insights.append({
        "type": "positive",
        "title": "Top Profit Product",
        "product": highest_profit["product_name"],
        "insight": (
            f'{highest_profit["product_name"]} generated '
            f'₹{highest_profit["profit"]:,.2f} in profit '
            f'with a '
            f'{highest_profit["profit_margin_percent"]:.2f}% '
            f'profit margin.'
        ),
        "business_impact": (
            "This product is a strong contributor to business profitability."
        )
    })

    # ---------------------------------------------------------
    # Insight 3 — Highest margin
    # ---------------------------------------------------------

    insights.append({
        "type": "positive",
        "title": "Highest Margin Product",
        "product": highest_margin["product_name"],
        "insight": (
            f'{highest_margin["product_name"]} has the highest '
            f'profit margin at '
            f'{highest_margin["profit_margin_percent"]:.2f}%.'
        ),
        "business_impact": (
            "High-margin products may provide better opportunities "
            "for profitable marketing and promotion."
        )
    })

    # ---------------------------------------------------------
    # Insight 4 — Lowest margin
    # ---------------------------------------------------------

    insights.append({
        "type": "warning",
        "title": "Lowest Margin Product",
        "product": lowest_margin["product_name"],
        "insight": (
            f'{lowest_margin["product_name"]} has the lowest '
            f'profit margin at '
            f'{lowest_margin["profit_margin_percent"]:.2f}%.'
        ),
        "business_impact": (
            "Low-margin products should be reviewed for pricing, "
            "discounting and cost efficiency."
        )
    })

    # ---------------------------------------------------------
    # Insight 5 — Product portfolio
    # ---------------------------------------------------------

    insights.append({
        "type": "summary",
        "title": "Product Portfolio Analysis",
        "insight": (
            f'The portfolio contains {len(star_products)} Star Products, '
            f'{len(revenue_traps)} Revenue Traps, '
            f'{len(growth_opportunities)} Growth Opportunities, and '
            f'{len(optimization_candidates)} Optimization Candidates.'
        ),
        "business_impact": (
            "This classification helps management decide where to "
            "increase investment, investigate profitability, or "
            "optimize the product portfolio."
        )
    })

    # ---------------------------------------------------------
    # Recommendation 1
    # ---------------------------------------------------------

    recommendations.append({
        "action": "Prioritize high-margin products",
        "priority": "High",
        "product": highest_margin["product_name"],
        "reason": (
            f'It has a {highest_margin["profit_margin_percent"]:.2f}% '
            "profit margin."
        ),
        "expected_impact": (
            "Potential improvement in profitability through "
            "better product promotion."
        )
    })

    # ---------------------------------------------------------
    # Recommendation 2
    # ---------------------------------------------------------

    recommendations.append({
        "action": "Review low-margin products",
        "priority": "Medium",
        "product": lowest_margin["product_name"],
        "reason": (
            f'Its profit margin is only '
            f'{lowest_margin["profit_margin_percent"]:.2f}%.'
        ),
        "expected_impact": (
            "Identify pricing, discount or cost issues affecting profit."
        )
    })

    # ---------------------------------------------------------
    # Recommendation 3 — Revenue traps
    # ---------------------------------------------------------

    if revenue_traps:
        recommendations.append({
            "action": "Investigate Revenue Trap products",
            "priority": "High",
            "reason": (
                f'{len(revenue_traps)} products generate high revenue '
                "but relatively low profit."
            ),
            "expected_impact": (
                "Improve profitability by reviewing pricing, "
                "discounts and product costs."
            )
        })

    # ---------------------------------------------------------
    # Recommendation 4 — Growth opportunities
    # ---------------------------------------------------------

    if growth_opportunities:
        recommendations.append({
            "action": "Evaluate Growth Opportunity products",
            "priority": "Medium",
            "reason": (
                f'{len(growth_opportunities)} products have strong '
                "profit potential but relatively low revenue."
            ),
            "expected_impact": (
                "Increasing visibility or marketing may help "
                "grow profitable sales."
            )
        })

    return {
        "insights": insights,
        "recommendations": recommendations
    }