# Enterprise Multi-Agent Business Intelligence (BI) Platform

Google Antigravity Enterprise BI Platform is a production-grade multi-agent workspace built on FastAPI, SQLAlchemy, ChromaDB, and LangGraph. It compiles natural language questions into query plans, generates secure SQL, aggregates analytical metrics, creates visualizations, predicts time-series forecasts, and exports downloadable PDF/Word/PPTX packages.

---

## Technical Stack Overview
- **Backend:** FastAPI, Python 3.12+, SQLAlchemy (Async), PostgreSQL/SQLite
- **Frontend:** Next.js / Vite React 19, TypeScript, Tailwind CSS, Zustand, Recharts, Plotly
- **Vector Database:** ChromaDB (Semantic Catalog, RAG Knowledge Base)
- **Multi-Agent Coordination:** LangGraph StateGraph (Shared State routing)
- **Caching:** Redis CacheManager
- **Forecasting Models:** ARIMA & Lag-Feature Random Forest Regressor

---

## Module Status Registry

| Module Name | Status | Key Classes / Files |
| :--- | :--- | :--- |
| **Authentication** | Completed | `auth.py` |
| **Database Connection Manager** | Completed | `ConnectionService`, `connection_service.py` |
| **Semantic Data Catalog** | Completed | `CatalogService`, `catalog_service.py` |
| **Query Planning Engine** | Completed | `QueryPlannerService`, `query_planner.py` |
| **SQL Generation & Optimizer** | Completed | `SQLAgentService`, `sql_agent_service.py` |
| **SQL Validation & Query Execution** | Completed | `QueryExecutionService`, `query_execution_service.py` |
| **Enterprise Analytics Agent** | Completed | `AnalyticsService`, `analytics_service.py` |
| **Enterprise Visualization Agent** | Completed | `VisualizationService`, `visualization_service.py` |
| **Enterprise Forecast Agent** | Completed | `ForecastService`, `forecast_service.py` |
| **Enterprise Recommendation Agent** | Completed | `RecommendationService`, `recommendation_service.py` |
| **Enterprise Report Agent** | Completed | `ReportService`, `report_service.py` |
| **LangGraph Multi-Agent Orchestrator** | Completed | `OrchestratorService`, `orchestrator_service.py` |
| **Enterprise RAG Knowledge Base** | Completed | `RAGService`, `rag_service.py` |
| **React 19 Frontend Web Client** | Completed | `frontend/src/` |

---

## Installation and Execution

### 1. Backend Application Setup
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Frontend Application Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. Run Test Suite
```bash
.venv\Scripts\pytest.exe
```
