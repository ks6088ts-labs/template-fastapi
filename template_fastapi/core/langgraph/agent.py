"""Main LangGraph agent interface."""

import uuid
from datetime import datetime
from typing import Any

from langchain_core.messages import HumanMessage

from .graph import get_compiled_graph
from .state import AgentState


class LangGraphAgent:
    """Main interface for LangGraph agent operations."""

    def __init__(self):
        self.graph = get_compiled_graph()

    def chat(self, message: str, thread_id: str | None = None) -> dict[str, Any]:
        """
        Chat with the LangGraph agent.
        
        Args:
            message: User message
            thread_id: Optional thread ID for conversation continuity
            
        Returns:
            Chat response with metadata
        """
        # Generate thread ID if not provided
        if thread_id is None:
            thread_id = str(uuid.uuid4())
        
        # Create initial state
        initial_state = AgentState(
            messages=[HumanMessage(content=message)],
            thread_id=thread_id,
            tools_used=[],
            step_count=0,
        )
        
        # Run the graph
        config = {"configurable": {"thread_id": thread_id}}
        result = self.graph.invoke(initial_state, config=config)
        
        # Extract the final response
        final_message = result["messages"][-1]
        response_content = final_message.content if hasattr(final_message, 'content') else str(final_message)
        
        return {
            "message": message,
            "response": response_content,
            "thread_id": thread_id,
            "tools_used": result.get("tools_used", []),
            "created_at": datetime.now().isoformat(),
            "step_count": result.get("step_count", 0),
        }

    def stream_chat(self, message: str, thread_id: str | None = None):
        """
        Stream chat with the LangGraph agent.
        
        Args:
            message: User message
            thread_id: Optional thread ID for conversation continuity
            
        Yields:
            Streaming responses from the agent
        """
        # Generate thread ID if not provided
        if thread_id is None:
            thread_id = str(uuid.uuid4())
        
        # Create initial state
        initial_state = AgentState(
            messages=[HumanMessage(content=message)],
            thread_id=thread_id,
            tools_used=[],
            step_count=0,
        )
        
        # Stream the graph execution
        config = {"configurable": {"thread_id": thread_id}}
        for chunk in self.graph.stream(initial_state, config=config):
            yield chunk