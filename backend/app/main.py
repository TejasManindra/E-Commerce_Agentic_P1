from fastapi import FastAPI

from app.api.kpi import router as kpi_router
from app.api.analytics import router as analytics_router
from app.api.category import router as category_router
from app.api.product import router as product_router
from app.api.root_cause import router as root_cause_router
from app.api.dashboard import router as dashboard_router
from app.api.query import router as query_router

app = FastAPI(
    title="E-Commerce Agentic BI",
    description="Agentic AI for E-Commerce Business Intelligence and Strategic Decision Support",
    version="1.0.0"
)


app.include_router(kpi_router)
app.include_router(analytics_router)
app.include_router(category_router)
app.include_router(product_router)
app.include_router(root_cause_router)
app.include_router(dashboard_router)
app.include_router(query_router)


@app.get("/")
def root():
    return {
        "message": "E-Commerce Agentic BI API is running",
        "status": "success"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }