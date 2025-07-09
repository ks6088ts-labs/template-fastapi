from datetime import datetime

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

from template_fastapi.models.agent import (
    AgentListResponse,
    AgentRequest,
    AgentResponse,
    AgentStatus,
    ChatRequest,
    ChatResponse,
)
from template_fastapi.settings.azure_ai_foundry import get_azure_ai_foundry_settings


class AgentRepository:
    """Repository for handling agent-related operations with Azure AI Foundry."""

    def __init__(self):
        self.settings = get_azure_ai_foundry_settings()
        self.client = AIProjectClient(
            self.settings.azure_ai_foundry_project_connection_string,
            credential=DefaultAzureCredential(),
        )

    def create_agent(self, request: AgentRequest) -> AgentResponse:
        """Create a new agent."""
        try:
            agent_response = self.client.agents.create_agent(
                model=request.model,
                name=request.name,
                description=request.description,
                instructions=request.instructions,
                tools=request.tools or [],
            )

            now = datetime.now().isoformat()

            return AgentResponse(
                id=agent_response.id,
                name=agent_response.name,
                description=agent_response.description,
                instructions=agent_response.instructions,
                model=agent_response.model,
                tools=agent_response.tools,
                status=AgentStatus.ACTIVE,
                created_at=now,
                updated_at=now,
            )
        except Exception as e:
            raise Exception(f"Failed to create agent: {str(e)}")

    def get_agent(self, agent_id: str) -> AgentResponse:
        """Get an agent by ID."""
        try:
            agent_response = self.client.agents.get_agent(agent_id)

            now = datetime.now().isoformat()

            return AgentResponse(
                id=agent_response.id,
                name=agent_response.name,
                description=agent_response.description,
                instructions=agent_response.instructions,
                model=agent_response.model,
                tools=agent_response.tools,
                status=AgentStatus.ACTIVE,
                created_at=now,
                updated_at=now,
            )
        except Exception as e:
            raise Exception(f"Failed to get agent: {str(e)}")

    def list_agents(self, limit: int = 10, offset: int = 0) -> AgentListResponse:
        """List agents."""
        try:
            agents_response = self.client.agents.list_agents()

            now = datetime.now().isoformat()

            agents = []
            for agent in agents_response.data:
                agents.append(
                    AgentResponse(
                        id=agent.id,
                        name=agent.name,
                        description=agent.description,
                        instructions=agent.instructions,
                        model=agent.model,
                        tools=agent.tools,
                        status=AgentStatus.ACTIVE,
                        created_at=now,
                        updated_at=now,
                    )
                )

            return AgentListResponse(
                agents=agents[offset : offset + limit],
                total=len(agents),
            )
        except Exception as e:
            raise Exception(f"Failed to list agents: {str(e)}")

    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent."""
        try:
            self.client.agents.delete_agent(agent_id)
            return True
        except Exception as e:
            raise Exception(f"Failed to delete agent: {str(e)}")

    def chat_with_agent(self, agent_id: str, request: ChatRequest) -> ChatResponse:
        """Chat with an agent."""
        try:
            # Create a thread if not provided
            if request.thread_id:
                thread_id = request.thread_id
            else:
                thread_response = self.client.agents.create_thread()
                thread_id = thread_response.id

            # Create a message
            message_response = self.client.agents.create_message(
                thread_id=thread_id,
                role="user",
                content=request.message,
            )

            # Create a run
            run_response = self.client.agents.create_run(
                thread_id=thread_id,
                assistant_id=agent_id,
            )

            # Poll for completion
            while run_response.status in ["queued", "in_progress"]:
                run_response = self.client.agents.get_run(
                    thread_id=thread_id,
                    run_id=run_response.id,
                )

            # Get the response
            messages = self.client.agents.list_messages(thread_id=thread_id)
            response_message = messages.data[0].content[0].text.value

            now = datetime.now().isoformat()

            return ChatResponse(
                id=message_response.id,
                agent_id=agent_id,
                thread_id=thread_id,
                message=request.message,
                response=response_message,
                created_at=now,
            )
        except Exception as e:
            raise Exception(f"Failed to chat with agent: {str(e)}")
