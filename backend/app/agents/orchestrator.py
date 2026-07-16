from langgraph.graph import StateGraph, END
from app.agents.state import AgentState

def orchestrator_node(state: AgentState) -> AgentState:
    return state

def sql_generator_node(state: AgentState) -> AgentState:
    return state

workflow = StateGraph(AgentState)
workflow.add_node("orchestrator", orchestrator_node)
workflow.add_node("sql_generator", sql_generator_node)

workflow.set_entry_point("orchestrator")
workflow.add_edge("orchestrator", "sql_generator")
workflow.add_edge("sql_generator", END)

agent_app = workflow.compile()
