"""Tests for LangGraph agent implementation."""

from fastapi.testclient import TestClient

from template_fastapi.app import app
from template_fastapi.internals.langgraph.tools import get_tools

client = TestClient(app)


def test_langgraph_tools_endpoint():
    """Test that the LangGraph tools endpoint returns available tools."""
    response = client.get("/agents/langgraph/tools")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert "total" in data
    assert isinstance(data["tools"], list)
    assert data["total"] == len(data["tools"])

    # Check tool structure
    if data["tools"]:
        tool = data["tools"][0]
        assert "name" in tool
        assert "description" in tool
        assert "args_schema" in tool


def test_get_tools_function():
    """Test that the get_tools function returns expected tools."""
    tools = get_tools()
    assert len(tools) == 3

    tool_names = [tool.name for tool in tools]
    assert "current_time" in tool_names
    assert "calculator" in tool_names
    assert "search" in tool_names


def test_calculator_tool():
    """Test the calculator tool functionality."""
    tools = get_tools()
    calc_tool = next(tool for tool in tools if tool.name == "calculator")

    # Test basic calculation
    result = calc_tool._run("2 + 3")
    assert "Result: 5" in result

    # Test multiplication
    result = calc_tool._run("4 * 5")
    assert "Result: 20" in result

    # Test invalid expression
    result = calc_tool._run("invalid")
    assert "Error calculating" in result


def test_current_time_tool():
    """Test the current time tool functionality."""
    tools = get_tools()
    time_tool = next(tool for tool in tools if tool.name == "current_time")

    result = time_tool._run()
    assert "Current time (UTC):" in result

    # Test with timezone parameter
    result = time_tool._run("JST")
    assert "Current time (JST):" in result


def test_search_tool():
    """Test the mock search tool functionality."""
    tools = get_tools()
    search_tool = next(tool for tool in tools if tool.name == "search")

    result = search_tool._run("test query")
    assert "Mock search results for 'test query'" in result
    assert "demonstration search tool" in result
