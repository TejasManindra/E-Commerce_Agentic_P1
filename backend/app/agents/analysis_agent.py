# ============================================================
# ANALYSIS AGENT
# ============================================================


def analyze_query_result(intent, rows):

    if not rows:

        return {
            "message": (
                "No data found for the selected period."
            )
        }

    # --------------------------------------------------------
    # CURRENT VS PREVIOUS PERIOD
    # --------------------------------------------------------

    if intent.comparison == "previous_period":

        current = 0.0

        previous = 0.0

        for row in rows:

            period = row.get("period")

            value = float(
                row.get("value") or 0
            )

            if period == "current":

                current = value

            elif period == "previous":

                previous = value

        if previous != 0:

            change_percent = (
                (current - previous)
                / abs(previous)
            ) * 100

        else:

            change_percent = 0.0

        if change_percent > 0:

            direction = "increased"

        elif change_percent < 0:

            direction = "decreased"

        else:

            direction = "remained stable"

        return {

            "current_value": round(
                current,
                2
            ),

            "previous_value": round(
                previous,
                2
            ),

            "change_percent": round(
                change_percent,
                2
            ),

            "direction": direction
        }

    # --------------------------------------------------------
    # DIMENSION ANALYSIS
    # --------------------------------------------------------

    findings = []

    for row in rows[:10]:

        findings.append({

            "dimension": row.get(
                "dimension"
            ),

            "value": float(
                row.get("value") or 0
            ),

            "profit": float(
                row.get("profit") or 0
            )
        })

    result = {

        "total_rows": len(rows),

        "findings": findings
    }

    if findings:

        result["top_dimension"] = (
            findings[0]
        )

    return result


# ============================================================
# ROOT CAUSE ANALYSIS
# ============================================================

def analyze_root_cause(rows):

    if not rows:

        return {
            "message": (
                "No root cause data found."
            )
        }

    findings = []

    # --------------------------------------------------------
    # ANALYZE EACH CATEGORY
    # --------------------------------------------------------

    for row in rows:

        category = row.get(
            "category"
        )

        current_revenue = float(
            row.get(
                "current_revenue"
            ) or 0
        )

        previous_revenue = float(
            row.get(
                "previous_revenue"
            ) or 0
        )

        current_profit = float(
            row.get(
                "current_profit"
            ) or 0
        )

        previous_profit = float(
            row.get(
                "previous_profit"
            ) or 0
        )

        current_discounts = float(
            row.get(
                "current_discounts"
            ) or 0
        )

        previous_discounts = float(
            row.get(
                "previous_discounts"
            ) or 0
        )

        current_returns = float(
            row.get(
                "current_returns"
            ) or 0
        )

        previous_returns = float(
            row.get(
                "previous_returns"
            ) or 0
        )

        # ----------------------------------------------------
        # REVENUE CHANGE
        # ----------------------------------------------------

        revenue_change = (
            current_revenue
            - previous_revenue
        )

        if previous_revenue != 0:

            revenue_change_percent = (
                revenue_change
                / abs(previous_revenue)
            ) * 100

        else:

            revenue_change_percent = 0.0

        # ----------------------------------------------------
        # PROFIT CHANGE
        # ----------------------------------------------------

        profit_change = (
            current_profit
            - previous_profit
        )

        if previous_profit != 0:

            profit_change_percent = (
                profit_change
                / abs(previous_profit)
            ) * 100

        else:

            profit_change_percent = 0.0

        # ----------------------------------------------------
        # PROFIT MARGIN
        # ----------------------------------------------------

        if current_revenue != 0:

            current_margin = (
                current_profit
                / current_revenue
            ) * 100

        else:

            current_margin = 0.0

        if previous_revenue != 0:

            previous_margin = (
                previous_profit
                / previous_revenue
            ) * 100

        else:

            previous_margin = 0.0

        margin_change = (
            current_margin
            - previous_margin
        )

        # ----------------------------------------------------
        # DISCOUNT CHANGE
        # ----------------------------------------------------

        discount_change = (
            current_discounts
            - previous_discounts
        )

        if previous_discounts != 0:

            discount_change_percent = (
                discount_change
                / abs(previous_discounts)
            ) * 100

        else:

            discount_change_percent = 0.0

        # ----------------------------------------------------
        # RETURN CHANGE
        # ----------------------------------------------------

        return_change = (
            current_returns
            - previous_returns
        )

        if previous_returns != 0:

            return_change_percent = (
                return_change
                / abs(previous_returns)
            ) * 100

        else:

            return_change_percent = 0.0

        # ----------------------------------------------------
        # DISCOUNT RATE
        # ----------------------------------------------------

        if current_revenue != 0:

            current_discount_rate = (
                current_discounts
                / current_revenue
            ) * 100

        else:

            current_discount_rate = 0.0

        if previous_revenue != 0:

            previous_discount_rate = (
                previous_discounts
                / previous_revenue
            ) * 100

        else:

            previous_discount_rate = 0.0

        discount_rate_change = (
            current_discount_rate
            - previous_discount_rate
        )

        # ----------------------------------------------------
        # RETURN RATE
        # ----------------------------------------------------

        if current_revenue != 0:

            current_return_rate = (
                current_returns
                / current_revenue
            ) * 100

        else:

            current_return_rate = 0.0

        if previous_revenue != 0:

            previous_return_rate = (
                previous_returns
                / previous_revenue
            ) * 100

        else:

            previous_return_rate = 0.0

        return_rate_change = (
            current_return_rate
            - previous_return_rate
        )

        # ----------------------------------------------------
        # STORE FINDING
        # ----------------------------------------------------

        findings.append({

            "category": category,

            "current_revenue": round(
                current_revenue,
                2
            ),

            "previous_revenue": round(
                previous_revenue,
                2
            ),

            "revenue_change": round(
                revenue_change,
                2
            ),

            "revenue_change_percent": round(
                revenue_change_percent,
                2
            ),

            "current_profit": round(
                current_profit,
                2
            ),

            "previous_profit": round(
                previous_profit,
                2
            ),

            "profit_change": round(
                profit_change,
                2
            ),

            "profit_change_percent": round(
                profit_change_percent,
                2
            ),

            "current_margin_percent": round(
                current_margin,
                2
            ),

            "previous_margin_percent": round(
                previous_margin,
                2
            ),

            "margin_change_percentage_points": round(
                margin_change,
                2
            ),

            "current_discounts": round(
                current_discounts,
                2
            ),

            "previous_discounts": round(
                previous_discounts,
                2
            ),

            "discount_change": round(
                discount_change,
                2
            ),

            "discount_change_percent": round(
                discount_change_percent,
                2
            ),

            "current_discount_rate_percent": round(
                current_discount_rate,
                2
            ),

            "previous_discount_rate_percent": round(
                previous_discount_rate,
                2
            ),

            "discount_rate_change_percentage_points": round(
                discount_rate_change,
                2
            ),

            "current_returns": round(
                current_returns,
                2
            ),

            "previous_returns": round(
                previous_returns,
                2
            ),

            "return_change": round(
                return_change,
                2
            ),

            "return_change_percent": round(
                return_change_percent,
                2
            ),

            "current_return_rate_percent": round(
                current_return_rate,
                2
            ),

            "previous_return_rate_percent": round(
                previous_return_rate,
                2
            ),

            "return_rate_change_percentage_points": round(
                return_rate_change,
                2
            )
        })

    # ========================================================
    # FIND CATEGORIES WITH PROFIT DECLINE
    # ========================================================

    declining_categories = [

        item

        for item in findings

        if item["profit_change"] < 0
    ]

    declining_categories.sort(
        key=lambda x: x["profit_change"]
    )

    # ========================================================
    # FIND LARGEST PROFIT CONTRIBUTOR TO DECLINE
    # ========================================================

    largest_profit_decline = None

    if declining_categories:

        largest_profit_decline = (
            declining_categories[0]
        )

    # ========================================================
    # FIND LOWEST CURRENT MARGIN
    # ========================================================

    lowest_margin_category = min(
        findings,
        key=lambda x: x[
            "current_margin_percent"
        ]
    ) if findings else None

    # ========================================================
    # FIND LARGEST DISCOUNT RATE INCREASE
    # ========================================================

    highest_discount_pressure = max(
        findings,
        key=lambda x: x[
            "discount_rate_change_percentage_points"
        ]
    ) if findings else None

    # ========================================================
    # FIND LARGEST RETURN RATE INCREASE
    # ========================================================

    highest_return_pressure = max(
        findings,
        key=lambda x: x[
            "return_rate_change_percentage_points"
        ]
    ) if findings else None

    return {

        "categories": findings,

        "profit_declining_categories":
            declining_categories,

        "largest_profit_decline":
            largest_profit_decline,

        "lowest_margin_category":
            lowest_margin_category,

        "highest_discount_pressure":
            highest_discount_pressure,

        "highest_return_pressure":
            highest_return_pressure
    }