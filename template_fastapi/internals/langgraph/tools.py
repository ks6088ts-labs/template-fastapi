"""Tools for LangGraph agent."""

import time

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class CurrentTimeInput(BaseModel):
    """Input for current time tool."""

    timezone: str = Field(default="UTC", description="Timezone to get time for")


class CalculatorInput(BaseModel):
    """Input for calculator tool."""

    expression: str = Field(description="Mathematical expression to evaluate")


class SearchInput(BaseModel):
    """Input for search tool."""

    query: str = Field(description="Search query")


class CurrentTimeTool(BaseTool):
    """Tool to get current time."""

    name: str = "current_time"
    description: str = "Get the current time. Useful for time-sensitive queries."
    args_schema: type[BaseModel] = CurrentTimeInput

    def _run(self, timezone: str = "UTC") -> str:
        """Get current time."""
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        return f"Current time ({timezone}): {current_time}"


class CalculatorTool(BaseTool):
    """Tool to perform calculations."""

    name: str = "calculator"
    description: str = "Perform mathematical calculations. Input should be a valid mathematical expression."
    args_schema: type[BaseModel] = CalculatorInput

    def _run(self, expression: str) -> str:
        """Evaluate mathematical expression."""
        try:
            # Safe evaluation of mathematical expressions
            # Remove any potentially dangerous functions/imports
            safe_dict = {
                "__builtins__": {},
                "abs": abs,
                "round": round,
                "min": min,
                "max": max,
                "pow": pow,
                "sum": sum,
            }
            result = eval(expression, safe_dict, {})
            return f"Result: {result}"
        except Exception as e:
            return f"Error calculating '{expression}': {str(e)}"


class MockSearchTool(BaseTool):
    """Mock search tool for demonstration."""

    name: str = "search"
    description: str = "Search for information on the internet. This is a mock tool for demonstration."
    args_schema: type[BaseModel] = SearchInput

    def _run(self, query: str) -> str:
        """Mock search function."""
        return f"Mock search results for '{query}': This is a demonstration search tool. In a real implementation, this would connect to a search API."  # noqa: E501


def get_tools() -> list[BaseTool]:
    """Get all available tools."""
    return [
        CurrentTimeTool(),
        CalculatorTool(),
        MockSearchTool(),
    ]
