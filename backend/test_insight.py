from app.agents.insight_agent import generate_product_insights


products = [
    {
        "product_name": "Electronics Computing Product 59",
        "revenue": 319249.20,
        "profit": 55703.16,
        "profit_margin_percent": 17.45
    },
    {
        "product_name": "Electronics Wearables Product 99",
        "revenue": 268395.41,
        "profit": 91145.31,
        "profit_margin_percent": 33.96
    }
]


result = generate_product_insights(products)

print(result)