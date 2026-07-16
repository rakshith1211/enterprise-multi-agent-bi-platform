from typing import Dict, Any, List, TypedDict, Optional

class AgentState(TypedDict):
    session_id: str
    user_query: str
    generated_sql: Optional[str]
    query_results: Optional[List[Dict[str, Any]]]
    python_code: Optional[str]
    chart_spec: Optional[Dict[str, Any]]
    final_report: Optional[str]
    errors: List[str]
