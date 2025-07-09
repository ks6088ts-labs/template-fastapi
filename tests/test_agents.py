import pytest
from unittest.mock import Mock, patch

from template_fastapi.models.agent import AgentRequest, AgentStatus
from template_fastapi.repositories.agents import AgentRepository


@pytest.fixture
def mock_ai_project_client():
    """Mock Azure AI Projects client."""
    with patch("template_fastapi.repositories.agents.AIProjectClient") as mock_client:
        yield mock_client


@pytest.fixture
def mock_agent_response():
    """Mock agent response from Azure AI Projects."""
    mock_response = Mock()
    mock_response.id = "test-agent-123"
    mock_response.name = "Test Agent"
    mock_response.description = "A test agent"
    mock_response.instructions = "Test instructions"
    mock_response.model = "gpt-4o"
    mock_response.tools = []
    return mock_response


def test_create_agent_success(mock_ai_project_client, mock_agent_response):
    """Test successful agent creation."""
    # Setup
    mock_client_instance = Mock()
    mock_ai_project_client.return_value = mock_client_instance
    mock_client_instance.agents.create_agent.return_value = mock_agent_response
    
    # Create repository and request
    repo = AgentRepository()
    request = AgentRequest(
        name="Test Agent",
        description="A test agent",
        instructions="Test instructions",
        model="gpt-4o"
    )
    
    # Execute
    result = repo.create_agent(request)
    
    # Verify
    assert result.id == "test-agent-123"
    assert result.name == "Test Agent"
    assert result.description == "A test agent"
    assert result.instructions == "Test instructions"
    assert result.model == "gpt-4o"
    assert result.status == AgentStatus.ACTIVE
    assert result.created_at is not None
    assert result.updated_at is not None
    
    # Verify API call
    mock_client_instance.agents.create_agent.assert_called_once_with(
        model="gpt-4o",
        name="Test Agent",
        description="A test agent",
        instructions="Test instructions",
        tools=[],
    )


def test_create_agent_failure(mock_ai_project_client):
    """Test agent creation failure."""
    # Setup
    mock_client_instance = Mock()
    mock_ai_project_client.return_value = mock_client_instance
    mock_client_instance.agents.create_agent.side_effect = Exception("API Error")
    
    # Create repository and request
    repo = AgentRepository()
    request = AgentRequest(name="Test Agent")
    
    # Execute and verify exception
    with pytest.raises(Exception) as exc_info:
        repo.create_agent(request)
    
    assert "Failed to create agent: API Error" in str(exc_info.value)


def test_get_agent_success(mock_ai_project_client, mock_agent_response):
    """Test successful agent retrieval."""
    # Setup
    mock_client_instance = Mock()
    mock_ai_project_client.return_value = mock_client_instance
    mock_client_instance.agents.get_agent.return_value = mock_agent_response
    
    # Create repository
    repo = AgentRepository()
    
    # Execute
    result = repo.get_agent("test-agent-123")
    
    # Verify
    assert result.id == "test-agent-123"
    assert result.name == "Test Agent"
    
    # Verify API call
    mock_client_instance.agents.get_agent.assert_called_once_with("test-agent-123")


def test_list_agents_success(mock_ai_project_client, mock_agent_response):
    """Test successful agent listing."""
    # Setup
    mock_client_instance = Mock()
    mock_ai_project_client.return_value = mock_client_instance
    
    mock_list_response = Mock()
    mock_list_response.data = [mock_agent_response]
    mock_client_instance.agents.list_agents.return_value = mock_list_response
    
    # Create repository
    repo = AgentRepository()
    
    # Execute
    result = repo.list_agents(limit=10, offset=0)
    
    # Verify
    assert result.total == 1
    assert len(result.agents) == 1
    assert result.agents[0].id == "test-agent-123"
    assert result.agents[0].name == "Test Agent"


def test_delete_agent_success(mock_ai_project_client):
    """Test successful agent deletion."""
    # Setup
    mock_client_instance = Mock()
    mock_ai_project_client.return_value = mock_client_instance
    mock_client_instance.agents.delete_agent.return_value = None
    
    # Create repository
    repo = AgentRepository()
    
    # Execute
    result = repo.delete_agent("test-agent-123")
    
    # Verify
    assert result is True
    mock_client_instance.agents.delete_agent.assert_called_once_with("test-agent-123")