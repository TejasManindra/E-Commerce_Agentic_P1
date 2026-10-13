import re
from dataclasses import dataclass
from datetime import date
from typing import Optional


# ============================================================
# QUERY INTENT
# ============================================================

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

    # Number of historical periods requested.
    # Example:
    # "previous 3 months" -> 3
    period_count: Optional[int] = None


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

        for keyword in METRIC_KEYWORDS[metric]:

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

    marketing_metrics = {

        "roas",
        "cac",
        "conversion_rate",

    }

    metric = _detect_metric(
        question_lower
    )

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
# PERIOD COUNT DETECTION
# ============================================================

def _detect_period_count(
    question: str,
) -> Optional[int]:

    question_lower = question.lower()

    number_words = {

        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,

    }

    # --------------------------------------------------------
    # Numeric forms
    #
    # previous 3 months
    # last 6 months
    # past 12 months
    # --------------------------------------------------------

    numeric_patterns = [

        r"\bprevious\s+(\d+)\s+months?\b",

        r"\bprior\s+(\d+)\s+months?\b",

        r"\blast\s+(\d+)\s+months?\b",

        r"\bpast\s+(\d+)\s+months?\b",

        r"\b(\d+)\s+previous\s+months?\b",

        r"\b(\d+)\s+prior\s+months?\b",

        r"\bprevious\s+(\d+)\s+weeks?\b",

        r"\blast\s+(\d+)\s+weeks?\b",

        r"\bpast\s+(\d+)\s+weeks?\b",

        r"\bprevious\s+(\d+)\s+years?\b",

        r"\blast\s+(\d+)\s+years?\b",

        r"\bpast\s+(\d+)\s+years?\b",

    ]

    for pattern in numeric_patterns:

        match = re.search(
            pattern,
            question_lower,
        )

        if match:

            try:

                count = int(
                    match.group(1)
                )

                if 2 <= count <= 24:

                    return count

            except ValueError:

                pass

    # --------------------------------------------------------
    # Word-number forms
    #
    # previous three months
    # last six months
    # --------------------------------------------------------

    for word, value in number_words.items():

        patterns = [

            rf"\bprevious\s+{word}\s+months?\b",

            rf"\bprior\s+{word}\s+months?\b",

            rf"\blast\s+{word}\s+months?\b",

            rf"\bpast\s+{word}\s+months?\b",

            rf"\b{word}\s+previous\s+months?\b",

        ]

        for pattern in patterns:

            if re.search(
                pattern,
                question_lower,
            ):

                return value

    return None


# ============================================================
# COMPARISON DETECTION
# ============================================================

def _detect_comparison(
    question: str,
) -> Optional[str]:

    question_lower = question.lower()

    period_count = _detect_period_count(
        question_lower
    )

    # Multi-period comparison must take priority.
    if period_count and period_count >= 2:

        return "previous_periods"

    comparison_phrases = [

        "previous period",

        "previous month",

        "previous week",

        "previous year",

        "prior period",

        "prior month",

        "prior week",

        "prior year",

        "last month",

        "last week",

        "last year",

        "month over month",

        "month-over-month",

        "week over week",

        "week-over-week",

        "year over year",

        "year-over-year",

        "mom",

        "wow",

        "yoy",

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

        "compare",

        "compared with",

        "compared to",

        "versus",

        "vs",

    ]

    if any(
        phrase in question_lower
        for phrase in comparison_phrases
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

    # --------------------------------------------------------
    # Multi-period trend
    # --------------------------------------------------------

    if comparison == "previous_periods":

        return "multi_period_trend_analysis"

    # --------------------------------------------------------
    # Marketing
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Standard comparison
    # --------------------------------------------------------

    if comparison == "previous_period":

        return f"{metric}_decline_analysis"

    # --------------------------------------------------------
    # Dimension analysis
    # --------------------------------------------------------

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
# MAIN QUERY UNDERSTANDING
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

    period_count = _detect_period_count(
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

    # Multi-period comparison is inherently monthly.
    if comparison == "previous_periods":

        dimension = "month"

    filters = {}

    if marketing_channel:

        filters["channel"] = (
            marketing_channel
        )

    return QueryIntent(

        original_question=question,

        intent=intent,

        metric=metric,

        dimension=dimension,

        start_date=start_date,

        end_date=end_date,

        comparison=comparison,

        filters=filters,

        period_count=period_count,

    )