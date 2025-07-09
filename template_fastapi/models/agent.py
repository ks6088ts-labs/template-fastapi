from enum import Enum
from typing import Any

from pydantic import BaseModel


class AgentStatus(str, Enum):
    """Agent status enumeration"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"


class AgentRequest(BaseModel):
    """Request model for creating an agent"""

    name: str
    description: str | None = None
    instructions: str | None = None
    model: str = "gpt-4o"
    tools: list[dict[str, Any]] | None = None


class AgentResponse(BaseModel):
    """Response model for agent operations"""

    id: str
    name: str
    description: str | None = None
    instructions: str | None = None
    model: str
    tools: list[dict[str, Any]] | None = None
    status: AgentStatus
    created_at: str
    updated_at: str


class ChatRequest(BaseModel):
    """Request model for chat with agent"""

    message: str
    thread_id: str | None = None


class ChatResponse(BaseModel):
    """Response model for chat with agent"""

    id: str
    agent_id: str
    thread_id: str
    message: str
    response: str
    created_at: str


class AgentListResponse(BaseModel):
    """Response model for listing agents"""

    agents: list[AgentResponse]
    total: int
