from fastapi import APIRouter
from app.api.connections.routes import router as connections_router
from app.api.catalog.routes import router as catalog_router
from app.api.planner.routes import router as planner_router
from app.api.sql.routes import router as sql_router
from app.api.query.routes import router as query_router
from app.api.analytics.routes import router as analytics_router
from app.api.visualization.routes import router as visualization_router
from app.api.forecast.routes import router as forecast_router
from app.api.recommendation.routes import router as recommendation_router
from app.api.report.routes import router as report_router
from app.api.orchestrator.routes import router as orchestrator_router
from app.api.rag.routes import router as rag_router

api_router = APIRouter()
api_router.include_router(connections_router, prefix="/connections", tags=["Connections"])
api_router.include_router(catalog_router, prefix="/catalog", tags=["Semantic Catalog"])
api_router.include_router(planner_router, prefix="/planner", tags=["Query Planner"])
api_router.include_router(sql_router, prefix="/sql", tags=["SQL Agent"])
api_router.include_router(query_router, prefix="/query", tags=["Query Execution Engine"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics Agent"])
api_router.include_router(visualization_router, prefix="/visualization", tags=["Visualization Agent"])
api_router.include_router(forecast_router, prefix="/forecast", tags=["Forecast Agent"])
api_router.include_router(recommendation_router, prefix="/recommendation", tags=["Recommendation Agent"])
api_router.include_router(report_router, prefix="/reports", tags=["Report Agent"])
api_router.include_router(orchestrator_router, prefix="/workflow", tags=["Orchestrator Agent"])
api_router.include_router(rag_router, prefix="/rag", tags=["RAG Knowledge Base"])
