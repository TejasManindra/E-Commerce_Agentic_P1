from typing import Any, Dict, List


def analyze_marketing_performance(
    rows: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Analyze marketing campaign performance.

    Expected fields:
        channel
        spend
        revenue_generated
        conversions
        new_customers
        impressions
        clicks
    """

    if not rows:
        return {
            "channels": [],
            "top_roas_channel": None,
            "lowest_roas_channel": None,
            "highest_spend_channel": None,
            "insights": []
        }

    channels = []

    for row in rows:

        channel = row.get("channel", "Unknown")

        spend = float(row.get("spend", 0) or 0)
        revenue = float(
            row.get("revenue_generated", 0) or 0
        )
        conversions = int(
            row.get("conversions", 0) or 0
        )
        new_customers = int(
            row.get("new_customers", 0) or 0
        )
        impressions = int(
            row.get("impressions", 0) or 0
        )
        clicks = int(
            row.get("clicks", 0) or 0
        )

        roas = (
            revenue / spend
            if spend > 0
            else 0
        )

        conversion_rate = (
            conversions / clicks * 100
            if clicks > 0
            else 0
        )

        customer_acquisition_cost = (
            spend / new_customers
            if new_customers > 0
            else 0
        )

        click_through_rate = (
            clicks / impressions * 100
            if impressions > 0
            else 0
        )

        channels.append({
            "channel": channel,
            "spend": spend,
            "revenue_generated": revenue,
            "conversions": conversions,
            "new_customers": new_customers,
            "impressions": impressions,
            "clicks": clicks,
            "roas": roas,
            "conversion_rate": conversion_rate,
            "customer_acquisition_cost":
                customer_acquisition_cost,
            "click_through_rate":
                click_through_rate
        })

    top_roas_channel = max(
        channels,
        key=lambda x: x["roas"]
    )

    lowest_roas_channel = min(
        channels,
        key=lambda x: x["roas"]
    )

    highest_spend_channel = max(
        channels,
        key=lambda x: x["spend"]
    )

    insights = []

    if top_roas_channel:
        insights.append({
            "type": "positive",
            "title": "Highest Marketing ROAS",
            "channel":
                top_roas_channel["channel"],
            "message": (
                f'{top_roas_channel["channel"]} '
                f'generated ROAS of '
                f'{top_roas_channel["roas"]:.2f}x.'
            )
        })

    if lowest_roas_channel:
        insights.append({
            "type": "warning",
            "title": "Lowest Marketing ROAS",
            "channel":
                lowest_roas_channel["channel"],
            "message": (
                f'{lowest_roas_channel["channel"]} '
                f'has the lowest ROAS at '
                f'{lowest_roas_channel["roas"]:.2f}x.'
            )
        })

    if highest_spend_channel:
        insights.append({
            "type": "info",
            "title": "Highest Marketing Spend",
            "channel":
                highest_spend_channel["channel"],
            "message": (
                f'{highest_spend_channel["channel"]} '
                f'has the highest spend of '
                f'₹{highest_spend_channel["spend"]:,.0f}.'
            )
        })

    return {
        "channels": channels,
        "top_roas_channel": top_roas_channel,
        "lowest_roas_channel":
            lowest_roas_channel,
        "highest_spend_channel":
            highest_spend_channel,
        "insights": insights
    }


def generate_marketing_recommendations(
    marketing_analysis: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Generate CEO-focused marketing recommendations.

    Recommendations consider:
    - ROAS
    - Spend
    - CAC
    - Conversion rate

    The function avoids blindly recommending
    scaling every high-ROAS channel.
    """

    recommendations = []

    channels = marketing_analysis.get(
        "channels",
        []
    )

    if not channels:
        return recommendations

    # ---------------------------------------------------------
    # CALCULATE BENCHMARKS
    # ---------------------------------------------------------

    total_spend = sum(
        float(channel.get("spend", 0) or 0)
        for channel in channels
    )

    total_revenue = sum(
        float(channel.get("revenue_generated", 0) or 0)
        for channel in channels
    )

    overall_roas = (
        total_revenue / total_spend
        if total_spend > 0
        else 0
    )

    # ---------------------------------------------------------
    # 1. HIGH SPEND + LOW ROAS
    # ---------------------------------------------------------

    for channel in channels:

        name = channel.get(
            "channel",
            "Unknown"
        )

        spend = float(
            channel.get("spend", 0) or 0
        )

        roas = float(
            channel.get("roas", 0) or 0
        )

        spend_share = (
            spend / total_spend * 100
            if total_spend > 0
            else 0
        )

        # Important: low efficiency combined
        # with meaningful spend.
        if (
            roas < overall_roas
            and spend_share >= 15
        ):

            recommendations.append({
                "action":
                    f"Review {name} marketing efficiency",

                "priority":
                    "High",

                "reason": (
                    f"{name} generated ROAS of "
                    f"{roas:.2f}x versus overall "
                    f"marketing ROAS of "
                    f"{overall_roas:.2f}x, "
                    f"while consuming "
                    f"{spend_share:.1f}% of total spend."
                ),

                "expected_impact":
                    "Improve marketing efficiency "
                    "and reduce inefficient spend.",

                "time_horizon":
                    "1-2 weeks",

                "owner":
                    "Marketing Manager"
            })

    # ---------------------------------------------------------
    # 2. HIGH CAC
    # ---------------------------------------------------------

    for channel in channels:

        name = channel.get(
            "channel",
            "Unknown"
        )

        cac = float(
            channel.get(
                "customer_acquisition_cost",
                0
            ) or 0
        )

        if cac > 50:

            recommendations.append({
                "action":
                    f"Reduce customer acquisition cost for {name}",

                "priority":
                    "Medium",

                "reason": (
                    f"Customer acquisition cost "
                    f"is ₹{cac:,.2f}."
                ),

                "expected_impact":
                    "Improve new-customer acquisition efficiency.",

                "time_horizon":
                    "2-4 weeks",

                "owner":
                    "Marketing / Growth Manager"
            })

    # ---------------------------------------------------------
    # 3. STRONG ROAS + MEANINGFUL SPEND
    # ---------------------------------------------------------

    for channel in channels:

        name = channel.get(
            "channel",
            "Unknown"
        )

        roas = float(
            channel.get("roas", 0) or 0
        )

        spend = float(
            channel.get("spend", 0) or 0
        )

        spend_share = (
            spend / total_spend * 100
            if total_spend > 0
            else 0
        )

        # Only identify a scaling candidate when
        # efficiency is strong AND the channel
        # already has meaningful spend.
        if (
            roas >= 4
            and spend_share >= 5
        ):

            recommendations.append({
                "action":
                    f"Evaluate controlled growth in {name}",

                "priority":
                    "Medium",

                "reason": (
                    f"ROAS is {roas:.2f}x with "
                    f"{spend_share:.1f}% of total "
                    "marketing spend."
                ),

                "expected_impact":
                    "Test additional profitable "
                    "customer acquisition.",

                "time_horizon":
                    "2-4 weeks",

                "owner":
                    "Marketing Manager"
            })

    # ---------------------------------------------------------
    # 4. LOW CONVERSION RATE
    # ---------------------------------------------------------

    for channel in channels:

        name = channel.get(
            "channel",
            "Unknown"
        )

        conversion_rate = float(
            channel.get(
                "conversion_rate",
                0
            ) or 0
        )

        if conversion_rate < 2:

            recommendations.append({
                "action":
                    f"Improve {name} conversion funnel",

                "priority":
                    "Medium",

                "reason": (
                    f"Conversion rate is "
                    f"{conversion_rate:.2f}%."
                ),

                "expected_impact":
                    "Increase conversions from existing traffic.",

                "time_horizon":
                    "2-4 weeks",

                "owner":
                    "Marketing / Growth Manager"
            })

    # ---------------------------------------------------------
    # 5. REMOVE DUPLICATE ACTIONS
    # ---------------------------------------------------------

    unique = []

    seen = set()

    for recommendation in recommendations:

        action = recommendation["action"]

        if action not in seen:

            seen.add(action)

            unique.append(
                recommendation
            )

    recommendations = unique

    # ---------------------------------------------------------
    # 6. PRIORITY ORDER
    # ---------------------------------------------------------

    priority_order = {
        "High": 1,
        "Medium": 2,
        "Low": 3
    }

    recommendations.sort(
        key=lambda x:
        priority_order.get(
            x.get("priority", "Low"),
            3
        )
    )

    # ---------------------------------------------------------
    # 7. CEO TOP 5
    # ---------------------------------------------------------

    return recommendations[:5]