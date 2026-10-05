import re
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class QueryIntent:
    original_question: str
    intent: str
    metric: str
    dimension: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    comparison: Optional[str] = None
    filters: Optional[dict] = None


# ============================================================
# METRIC KEYWORDS
# ============================================================

METRIC_KEYWORDS = {
    "profit": [
        "profit",
        "profits",
        "profitability",
        "margin",
    ],

    "revenue": [
        "revenue",
        "sales",
        "sales value",
    ],

    "orders": [
        "orders",
        "order count",
        "order volume",
    ],

    "customers": [
        "customers",
        "customer",
        "buyers",
    ],

    "units_sold": [
        "units",
        "units sold",
        "quantity",
        "volume sold",
    ],

    "discounts": [
        "discount",
        "discounts",
        "discounting",
    ],

    "roas": [
        "roas",
        "return on ad spend",
        "advertising return",
        "ad return",
        "ad efficiency",
        "advertising efficiency",
        "marketing efficiency",
    ],

    "cac": [
        "cac",
        "customer acquisition cost",
        "acquisition cost",
        "cost per customer",
    ],

    "conversion_rate": [
        "conversion rate",
        "conversion rates",
        "conversions",
        "conversion",
    ],
}


# ============================================================
# DIMENSION KEYWORDS
# ============================================================

DIMENSION_KEYWORDS = {
    "category": [
        "category",
        "categories",
    ],

    "product": [
        "product",
        "products",
        "sku",
        "skus",
    ],

    "state": [
        "state",
        "states",
        "location",
        "geography",
        "geographic",
    ],

    "channel": [
        "channel",
        "channels",
        "marketing channel",
        "ad channel",
        "advertising channel",
    ],

    "month": [
        "month",
        "monthly",
        "trend",
        "trends",
    ],
}


# ============================================================
# KNOWN MARKETING CHANNELS
# ============================================================

MARKETING_CHANNELS = [
    "google ads",
    "meta ads",
    "instagram",
    "marketplace",
    "affiliate",
    "influencer",
    "email",
    "organic search",
]


# ============================================================
# METRIC DETECTION
# ============================================================

def _detect_metric(question: str) -> str:

    question_lower = question.lower()

    # Check longer / more specific phrases first.
    ordered_metrics = [
        "conversion_rate",
        "roas",
        "cac",
        "profit",
        "revenue",
        "orders",
        "customers",
        "units_sold",
        "discounts",
    ]

    for metric in ordered_metrics:

        keywords = METRIC_KEYWORDS[metric]

        for keyword in keywords:

            if keyword in question_lower:
                return metric

    return "revenue"


# ============================================================
# DIMENSION DETECTION
# ============================================================

def _detect_dimension(
    question: str,
) -> Optional[str]:

    question_lower = question.lower()

    # Marketing metrics imply channel analysis
    # even when the user does not explicitly say
    # the word "channel".
    marketing_metrics = {
        "roas",
        "cac",
        "conversion_rate",
    }

    metric = _detect_metric(question_lower)

    if metric in marketing_metrics:

        for channel in MARKETING_CHANNELS:

            if channel in question_lower:
                return "channel"

    for dimension, keywords in DIMENSION_KEYWORDS.items():

        for keyword in keywords:

            if keyword in question_lower:
                return dimension

    return None


# ============================================================
# MARKETING CHANNEL DETECTION
# ============================================================

def _detect_marketing_channel(
    question: str,
) -> Optional[str]:

    question_lower = question.lower()

    for channel in MARKETING_CHANNELS:

        if channel in question_lower:
            return channel

    return None


# ============================================================
# COMPARISON DETECTION
# ============================================================

def _detect_comparison(
    question: str,
) -> Optional[str]:

    question_lower = question.lower()

    comparison_words = [
        "why did",
        "why has",
        "why was",
        "why is",
        "decrease",
        "decreased",
        "decline",
        "declined",
        "drop",
        "dropped",
        "fall",
        "fell",
        "increase",
        "increased",
        "growth",
        "grew",
        "change",
        "changed",
        "down",
        "up",
        "lower",
        "higher",
        "worse",
        "better",
    ]

    if any(
        word in question_lower
        for word in comparison_words
    ):
        return "previous_period"

    return None


# ============================================================
# INTENT DETECTION
# ============================================================

def _detect_intent(
    metric: str,
    dimension: Optional[str],
    comparison: Optional[str],
    marketing_channel: Optional[str],
) -> str:

    # Marketing analysis takes priority.
    if metric in {
        "roas",
        "cac",
        "conversion_rate",
    }:

        if marketing_channel:

            if comparison == "previous_period":
                return "marketing_channel_comparison"

            return "marketing_channel_analysis"

        if dimension == "channel":

            if comparison == "previous_period":
                return "marketing_channel_comparison"

            return "marketing_channel_analysis"

        return "marketing_analysis"

    # Standard business analysis.
    if comparison == "previous_period":

        return f"{metric}_decline_analysis"

    if (
        dimension == "category"
        and metric == "revenue"
    ):
        return "category_revenue_analysis"

    if dimension == "product":

        return "product_performance_analysis"

    if dimension == "state":

        return "geography_analysis"

    if dimension == "channel":

        return "channel_analysis"

    if dimension == "month":

        return "monthly_trend_analysis"

    return "metric_analysis"


# ============================================================
# MAIN QUERY UNDERSTANDING FUNCTION
# ============================================================

def understand_query(
    question: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> QueryIntent:

    question = question.strip()

    question_lower = question.lower()

    metric = _detect_metric(
        question_lower
    )

    dimension = _detect_dimension(
        question_lower
    )

    comparison = _detect_comparison(
        question_lower
    )

    marketing_channel = (
        _detect_marketing_channel(
            question_lower
        )
    )

    intent = _detect_intent(
        metric=metric,
        dimension=dimension,
        comparison=comparison,
        marketing_channel=marketing_channel,
    )

    filters = {}

    if marketing_channel:

        filters["channel"] = marketing_channel

    return QueryIntent(
        original_question=question,

        intent=intent,

        metric=metric,

        dimension=dimension,

        start_date=start_date,

        end_date=end_date,

        comparison=comparison,

        filters=filters,
    )