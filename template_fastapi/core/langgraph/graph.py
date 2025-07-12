"""Graph definition for LangGraph agent workflow."""

from langgraph.graph import StateGraph, END

from .nodes import agent_node, tool_node, should_continue
from .state import AgentState


def create_graph() -> StateGraph:
    """
    Create the LangGraph workflow graph.
    
    Returns:
        Compiled graph ready for execution
    """
    # Create the state graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END,
        }
    )
    
    # Add edge from tools back to agent
    workflow.add_edge("tools", "agent")
    
    # Compile the graph
    return workflow.compile()


def get_compiled_graph() -> StateGraph:
    """Get a compiled instance of the workflow graph."""
    return create_graph()