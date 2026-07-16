from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict, total=False):
    user_query: str
    connection_id: str
    generate_report: bool
    query_plan: Dict[str, Any]
    sql: str
    query_results: Dict[str, Any]
    analytics: Dict[str, Any]
    visualization: Dict[str, Any]
    forecast: Dict[str, Any]
    recommendations: Dict[str, Any]
    report: Dict[str, Any]
    errors: List[str]
    trace: List[str]
