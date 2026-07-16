from typing import Callable, Dict, List, Any, Optional
import logging
from app.services.orchestrator.state import AgentState

logger = logging.getLogger(__name__)

class StateGraph:
    def __init__(self, state_schema: Any):
        self.state_schema = state_schema
        self.nodes = {}
        self.edges = []
        self.conditional_edges = []
        
    def add_node(self, name: str, node_func: Callable):
        self.nodes[name] = node_func
        
    def add_edge(self, source: str, target: str):
        self.edges.append((source, target))
        
    def add_conditional_edges(self, source: str, routing_func: Callable, mapping: Dict[str, str]):
        self.conditional_edges.append((source, routing_func, mapping))
        
    def compile(self):
        # Validation checks
        logger.info(f"StateGraph compiled with nodes: {list(self.nodes.keys())}")
        return CompiledGraph(self)

class CompiledGraph:
    def __init__(self, graph: StateGraph):
        self.graph = graph
        
    async def invoke(self, initial_state: AgentState) -> AgentState:
        state = dict(initial_state)
        if "trace" not in state:
            state["trace"] = []
        if "errors" not in state:
            state["errors"] = []
            
        current_node = "planner" # entry point
        
        while current_node and current_node != "end":
            state["trace"].append(current_node)
            logger.info(f"Executing orchestrator node: {current_node}")
            
            # 1. Execute current node
            node_func = self.graph.nodes.get(current_node)
            if not node_func:
                logger.error(f"Node {current_node} func not registered in graph.")
                break
                
            try:
                # Node mutation returns state diff dict
                diff = await node_func(state)
                state.update(diff)
            except Exception as e:
                logger.error(f"Orchestrator node execution error at {current_node}: {e}")
                state["errors"].append(f"Node {current_node} failed: {str(e)}")
                # Error recovery: Route directly to aggregator
                current_node = "aggregator"
                continue

            # 2. Check conditional edges
            next_node = None
            for src, route_fn, mapping in self.graph.conditional_edges:
                if src == current_node:
                    route_result = route_fn(state)
                    next_node = mapping.get(route_result)
                    break
            
            # 3. Check normal edges if no conditional route
            if not next_node:
                for src, dest in self.graph.edges:
                    if src == current_node:
                        next_node = dest
                        break
            
            current_node = next_node
            
        return state
