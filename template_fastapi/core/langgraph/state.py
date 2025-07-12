"""State definition for LangGraph agent workflow."""

from typing import Annotated, Sequence

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel


class AgentState(BaseModel):
    """State for the agent workflow."""

    # The add_messages function defines how to update the message list
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
    # Additional state for tool usage tracking
    tools_used: list[str] = []
    
    # Conversation metadata
    thread_id: str | None = None
    step_count: int = 0