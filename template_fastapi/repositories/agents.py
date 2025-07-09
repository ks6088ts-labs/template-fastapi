from datetime import datetime

from azure.ai.agents.models import CodeInterpreterTool
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

from template_fastapi.models.agent import (
    AgentListResponse,
    AgentRequest,
    AgentResponse,
    AgentStatus,
    ChatRequest,
    ChatResponse,
    ThreadListResponse,
    ThreadRequest,
    ThreadResponse,
)
from template_fastapi.settings.azure_ai_foundry import get_azure_ai_foundry_settings

code_interpreter = CodeInterpreterTool()


class AgentRepository:
    """Repository for handling agent-related operations with Azure AI Foundry."""

    def __init__(self):
        self.settings = get_azure_ai_foundry_settings()
        self.client = AIProjectClient(
            endpoint=self.settings.azure_ai_foundry_project_endpoint,
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
                tools=code_interpreter.definitions,
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

    def list_agents(self, limit: int = 10) -> AgentListResponse:
        """List agents."""
        try:
            agents_response = self.client.agents.list_agents(
                limit=limit,
            )

            now = datetime.now().isoformat()

            agents = []
            for agent in agents_response:
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
                agents=agents,
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
            _ = self.client.agents.messages.create(
                thread_id=request.thread_id,
                role="user",
                content=request.message,
            )

            run = self.client.agents.runs.create_and_process(
                agent_id=agent_id,
                thread_id=request.thread_id,
            )

            print(f"Run ID: {run.id}m status: {run.last_error}")

            messages = self.client.agents.messages.list(
                thread_id=request.thread_id,
            )

            # FIXME: Iterable object の最初のメッセージを取得
            for message in messages:
                return ChatResponse(
                    id=run.id,
                    agent_id=agent_id,
                    thread_id=request.thread_id,
                    message=request.message,
                    response=message.content.__str__() if messages else "",
                    created_at=message.created_at.isoformat() if messages else "",
                )

        except Exception as e:
            raise Exception(f"Failed to chat with agent: {str(e)}")

    def create_thread(self, request: ThreadRequest) -> ThreadResponse:
        """Create a new thread for chatting with an agent."""
        try:
            thread_response = self.client.agents.threads.create(**request.model_dump())
            return ThreadResponse(
                id=thread_response.id,
                created_at=thread_response.created_at.isoformat(),
            )
        except Exception as e:
            raise Exception(f"Failed to create thread: {str(e)}")

    def get_thread(self, thread_id: str) -> ThreadResponse:
        """Get a specific thread by ID."""
        try:
            thread_response = self.client.agents.threads.get(thread_id=thread_id)
            return ThreadResponse(
                id=thread_response.id,
                created_at=thread_response.created_at.isoformat(),
            )
        except Exception as e:
            raise Exception(f"Failed to get thread: {str(e)}")

    def delete_thread(self, thread_id: str) -> bool:
        """Delete a specific thread by ID."""
        try:
            self.client.agents.threads.delete(thread_id=thread_id)
            return True
        except Exception as e:
            raise Exception(f"Failed to delete thread: {str(e)}")

    def list_threads(self, limit: int) -> ThreadListResponse:
        """List threads for a specific agent."""
        try:
            threads_response = self.client.agents.threads.list(limit=limit)
            threads = []
            for thread in threads_response:
                threads.append(
                    ThreadResponse(
                        id=thread.id,
                        created_at=thread.created_at.isoformat(),
                    )
                )
            return ThreadListResponse(
                threads=threads,
                total=len(threads),
            )
        except Exception as e:
            raise Exception(f"Failed to list threads: {str(e)}")
