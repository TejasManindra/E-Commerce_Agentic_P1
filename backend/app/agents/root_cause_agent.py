def analyze_root_cause(product):
    revenue = product["revenue"]
    profit = product["profit"]
    margin = product["profit_margin_percent"]
    cost = product.get("cost", 0)
    discount = product.get("discount", 0)
    returns = product.get("returns", 0)

    causes = []

    if margin < 0:
        causes.append({
            "factor": "Negative profitability",
            "evidence": f"Profit margin is {margin:.2f}%",
            "impact": "The product is generating a loss."
        })

    if cost > revenue and revenue > 0:
        causes.append({
            "factor": "High product cost",
            "evidence": f"Cost ₹{cost:,.2f} exceeds revenue ₹{revenue:,.2f}",
            "impact": "Product cost is consuming more than the generated revenue."
        })

    if discount > 0:
        causes.append({
            "factor": "Discounting",
            "evidence": f"Discount amount is ₹{discount:,.2f}",
            "impact": "Discounts may be reducing product profitability."
        })

    if returns > 0:
        causes.append({
            "factor": "Product returns",
            "evidence": f"Return value is ₹{returns:,.2f}",
            "impact": "Returns can reduce realized profitability."
        })

    if not causes:
        causes.append({
            "factor": "Further investigation required",
            "evidence": "Available product-level metrics do not identify a clear cause.",
            "impact": "Pricing, costs, discounts and returns should be investigated."
        })

    if margin < 0:
        recommendation = "Review product pricing, cost structure and discount strategy immediately."
        priority = "Critical"
    elif margin < 10:
        recommendation = "Review pricing and promotional discounts."
        priority = "High"
    else:
        recommendation = "Continue monitoring product profitability."
        priority = "Medium"

    return {
        "product": product["product_name"],
        "problem": (
            f"Product has a profit margin of {margin:.2f}%."
        ),
        "root_causes": causes,
        "recommendation": recommendation,
        "priority": priority
    }