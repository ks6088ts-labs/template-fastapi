"""LangGraph-based agent API router."""

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from template_fastapi.core.langgraph.agent import LangGraphAgent
from template_fastapi.models.agent import LangGraphChatRequest, LangGraphChatResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize the LangGraph agent
langgraph_agent = LangGraphAgent()


@router.post("/chat", response_model=LangGraphChatResponse)
async def chat_with_langgraph_agent(request: LangGraphChatRequest) -> LangGraphChatResponse:
    """
    Chat with the LangGraph-based agent.
    
    Args:
        request: Chat request with message and optional thread_id
        
    Returns:
        Chat response with agent's reply and metadata
    """
    try:
        logger.info(f"LangGraph chat request: {request.message[:100]}...")
        
        # Use the LangGraph agent to process the message
        result = langgraph_agent.chat(
            message=request.message,
            thread_id=request.thread_id,
        )
        
        response = LangGraphChatResponse(
            message=result["message"],
            response=result["response"],
            thread_id=result["thread_id"],
            tools_used=result["tools_used"],
            created_at=result["created_at"],
        )
        
        logger.info(f"LangGraph chat response generated for thread: {response.thread_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error in LangGraph chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@router.post("/chat/stream")
async def stream_chat_with_langgraph_agent(request: LangGraphChatRequest):
    """
    Stream chat with the LangGraph-based agent.
    
    Args:
        request: Chat request with message and optional thread_id
        
    Returns:
        Streaming response with agent's replies
    """
    try:
        logger.info(f"LangGraph stream chat request: {request.message[:100]}...")
        
        def generate():
            try:
                for chunk in langgraph_agent.stream_chat(
                    message=request.message,
                    thread_id=request.thread_id,
                ):
                    yield f"data: {chunk}\n\n"
            except Exception as e:
                logger.error(f"Error in streaming: {str(e)}")
                yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except Exception as e:
        logger.error(f"Error in LangGraph stream chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Stream chat processing failed: {str(e)}")


@router.get("/tools")
async def get_available_tools():
    """
    Get list of available tools for the LangGraph agent.
    
    Returns:
        List of available tools with their descriptions
    """
    try:
        from template_fastapi.core.langgraph.tools import get_tools
        
        tools = get_tools()
        tool_info = []
        
        for tool in tools:
            tool_info.append({
                "name": tool.name,
                "description": tool.description,
                "args_schema": tool.args_schema.model_json_schema() if tool.args_schema else None,
            })
        
        return {
            "tools": tool_info,
            "total": len(tool_info),
        }
        
    except Exception as e:
        logger.error(f"Error getting tools: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get tools: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint for LangGraph agent service.
    
    Returns:
        Service health status
    """
    return {
        "status": "healthy",
        "service": "langgraph-agent",
        "timestamp": datetime.now().isoformat(),
    }