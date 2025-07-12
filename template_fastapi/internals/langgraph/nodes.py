"""Graph nodes for LangGraph agent workflow."""

from langchain_core.messages import ToolMessage

from .llms import LLMFactory
from .states import AgentState
from .tools import get_tools


def agent_node(state: AgentState) -> dict:
    """
    Agent node that processes messages and decides whether to use tools.

    Args:
        state: Current workflow state

    Returns:
        Updated state with LLM response
    """
    # Get the LLM instance
    llm = LLMFactory.get_llm()

    # Bind tools to the LLM
    tools = get_tools()
    llm_with_tools = llm.bind_tools(tools)

    # Get the last user message
    messages = state.messages

    # Invoke the LLM
    response = llm_with_tools.invoke(messages)

    # Track tools used if any
    tools_used = []
    if hasattr(response, "tool_calls") and response.tool_calls:
        tools_used = [tool_call["name"] for tool_call in response.tool_calls]

    return {
        "messages": [response],
        "tools_used": state.tools_used + tools_used,
        "step_count": state.step_count + 1,
    }


def tool_node(state: AgentState) -> dict:
    """
    Tool execution node that runs the tools requested by the agent.

    Args:
        state: Current workflow state

    Returns:
        Updated state with tool results
    """
    tools_by_name = {tool.name: tool for tool in get_tools()}

    # Get the last message from the agent
    last_message = state.messages[-1]

    # Execute tool calls if any
    tool_messages = []
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            if tool_name in tools_by_name:
                tool = tools_by_name[tool_name]
                try:
                    result = tool.invoke(tool_args)
                    tool_messages.append(
                        ToolMessage(
                            content=str(result),
                            tool_call_id=tool_call["id"],
                        )
                    )
                except Exception as e:
                    tool_messages.append(
                        ToolMessage(
                            content=f"Error executing {tool_name}: {str(e)}",
                            tool_call_id=tool_call["id"],
                        )
                    )
            else:
                tool_messages.append(
                    ToolMessage(
                        content=f"Unknown tool: {tool_name}",
                        tool_call_id=tool_call["id"],
                    )
                )

    return {
        "messages": tool_messages,
        "step_count": state.step_count + 1,
    }


def should_continue(state: AgentState) -> str:
    """
    Conditional edge function to determine if the workflow should continue.

    Args:
        state: Current workflow state

    Returns:
        Next node to execute or "end"
    """
    # Get the last message
    last_message = state.messages[-1]

    # If the last message has tool calls, execute tools
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    # Otherwise, end the workflow
    return "end"
