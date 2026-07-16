from typing import Any
from app.services.orchestrator.graph import StateGraph
from app.services.orchestrator.state import AgentState
from app.services.orchestrator.nodes import (
    planner_node, sql_agent_node, execution_node, analytics_node,
    visualization_node, forecast_node, recommendation_node, report_node, aggregator_node
)
from sqlalchemy.ext.asyncio import AsyncSession

def compile_agent_workflow(db: AsyncSession) -> Any:
    workflow = StateGraph(AgentState)
    
    # Register Node lambdas mapping db session dependency injection
    workflow.add_node("planner", lambda state: planner_node(state, db))
    workflow.add_node("sql_agent", lambda state: sql_agent_node(state, db))
    workflow.add_node("execution", lambda state: execution_node(state, db))
    workflow.add_node("analytics", lambda state: analytics_node(state, db))
    workflow.add_node("visualization", lambda state: visualization_node(state, db))
    workflow.add_node("forecast", lambda state: forecast_node(state, db))
    workflow.add_node("recommendation", lambda state: recommendation_node(state, db))
    workflow.add_node("report", lambda state: report_node(state, db))
    workflow.add_node("aggregator", lambda state: aggregator_node(state, db))
    
    # 1. Standard edges
    workflow.add_edge("planner", "sql_agent")
    workflow.add_edge("sql_agent", "execution")
    workflow.add_edge("execution", "analytics")
    workflow.add_edge("analytics", "visualization")
    
    # 2. Conditional edge from visualization to forecast
    def route_after_visualization(state: AgentState) -> str:
        # Check if columns indicate temporal metrics
        cols = [c.lower() for c in state.get("query_results", {}).get("columns", [])]
        has_time = any(t in cols for t in ["month", "date", "year", "time"])
        return "route_forecast" if has_time else "route_recommendation"
        
    workflow.add_conditional_edges(
        "visualization",
        route_after_visualization,
        {
            "route_forecast": "forecast",
            "route_recommendation": "recommendation"
        }
    )
    
    # 3. Normal edge from forecast to recommendation
    workflow.add_edge("forecast", "recommendation")
    
    # 4. Conditional edge from recommendation to report
    def route_after_recommendation(state: AgentState) -> str:
        return "route_report" if state.get("generate_report") else "route_aggregator"
        
    workflow.add_conditional_edges(
        "recommendation",
        route_after_recommendation,
        {
            "route_report": "report",
            "route_aggregator": "aggregator"
        }
    )
    
    workflow.add_edge("report", "aggregator")
    workflow.add_edge("aggregator", "end")
    
    return workflow.compile()
