from fastapi import APIRouter, HTTPException, Query

from template_fastapi.models.agent import (
    AgentListResponse,
    AgentRequest,
    AgentResponse,
    ChatRequest,
    ChatResponse,
    ThreadListResponse,
    ThreadRequest,
    ThreadResponse,
)
from template_fastapi.repositories.agents import AgentRepository
from template_fastapi.settings.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()
agent_repo = AgentRepository()


@router.post(
    "/",
    response_model=AgentResponse,
    operation_id="create_agent",
)
async def create_agent(request: AgentRequest) -> AgentResponse:
    """
    新しいエージェントを作成する
    """
    logger.info(f"Creating new agent with model: {request.model}")
    try:
        result = agent_repo.create_agent(request)
        logger.info(f"Successfully created agent with ID: {result.id}")
        return result
    except Exception as e:
        logger.error(f"Failed to create agent: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"エージェントの作成に失敗しました: {str(e)}")


@router.get(
    "/{agent_id}",
    response_model=AgentResponse,
    operation_id="get_agent",
)
async def get_agent(agent_id: str) -> AgentResponse:
    """
    エージェントの情報を取得する
    """
    logger.info(f"Getting agent: {agent_id}")
    try:
        result = agent_repo.get_agent(agent_id)
        logger.debug(f"Successfully retrieved agent: {agent_id}")
        return result
    except Exception as e:
        logger.warning(f"Agent not found: {agent_id} - {str(e)}")
        raise HTTPException(status_code=404, detail=f"エージェントが見つかりません: {str(e)}")


@router.get(
    "/",
    response_model=AgentListResponse,
    operation_id="list_agents",
)
async def list_agents(
    limit: int = Query(default=10, ge=1, le=100, description="取得する件数"),
) -> AgentListResponse:
    """
    エージェントの一覧を取得する
    """
    logger.info(f"Listing agents with limit: {limit}")
    try:
        result = agent_repo.list_agents(limit=limit)
        logger.info(f"Retrieved {len(result.agents)} agents")
        return result
    except Exception as e:
        logger.error(f"Failed to list agents: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"エージェント一覧の取得に失敗しました: {str(e)}")


@router.delete(
    "/{agent_id}",
    operation_id="delete_agent",
)
async def delete_agent(agent_id: str) -> dict:
    """
    エージェントを削除する
    """
    logger.info(f"Deleting agent: {agent_id}")
    try:
        success = agent_repo.delete_agent(agent_id)
        if success:
            logger.info(f"Successfully deleted agent: {agent_id}")
            return {"message": "エージェントが正常に削除されました"}
        else:
            logger.error(f"Failed to delete agent (no error): {agent_id}")
            raise HTTPException(status_code=500, detail="エージェントの削除に失敗しました")
    except Exception as e:
        logger.error(f"Failed to delete agent {agent_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"エージェントの削除に失敗しました: {str(e)}")


@router.post(
    "/{agent_id}/chat",
    response_model=ChatResponse,
    operation_id="chat_with_agent",
)
async def chat_with_agent(agent_id: str, request: ChatRequest) -> ChatResponse:
    """
    エージェントとチャットする
    """
    logger.info(f"Starting chat with agent {agent_id} on thread {request.thread_id}")
    logger.debug(f"Chat message: {request.message[:100]}...")  # Log first 100 chars
    try:
        result = agent_repo.chat_with_agent(agent_id, request)
        logger.info(f"Chat completed successfully with agent {agent_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to chat with agent {agent_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"エージェントとのチャットに失敗しました: {str(e)}")


@router.post(
    "/threads/",
    response_model=ThreadResponse,
    operation_id="create_thread",
)
async def create_thread(request: ThreadRequest) -> ThreadResponse:
    """
    新しいスレッドを作成する
    """
    logger.info("Creating new thread")
    try:
        result = agent_repo.create_thread(request)
        logger.info(f"Successfully created thread with ID: {result.id}")
        return result
    except Exception as e:
        logger.error(f"Failed to create thread: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"スレッドの作成に失敗しました: {str(e)}")


@router.get(
    "/threads/{thread_id}",
    response_model=ThreadResponse,
    operation_id="get_thread",
)
async def get_thread(thread_id: str) -> ThreadResponse:
    """
    スレッドの情報を取得する
    """
    logger.info(f"Getting thread: {thread_id}")
    try:
        result = agent_repo.get_thread(thread_id)
        logger.debug(f"Successfully retrieved thread: {thread_id}")
        return result
    except Exception as e:
        logger.warning(f"Thread not found: {thread_id} - {str(e)}")
        raise HTTPException(status_code=404, detail=f"スレッドが見つかりません: {str(e)}")


@router.delete(
    "/threads/{thread_id}",
    operation_id="delete_thread",
)
async def delete_thread(thread_id: str) -> dict:
    """
    スレッドを削除する
    """
    logger.info(f"Deleting thread: {thread_id}")
    try:
        success = agent_repo.delete_thread(thread_id)
        if success:
            logger.info(f"Successfully deleted thread: {thread_id}")
            return {"message": "スレッドが正常に削除されました"}
        else:
            logger.error(f"Failed to delete thread (no error): {thread_id}")
            raise HTTPException(status_code=500, detail="スレッドの削除に失敗しました")
    except Exception as e:
        logger.error(f"Failed to delete thread {thread_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"スレッドの削除に失敗しました: {str(e)}")


@router.get(
    "/threads/",
    response_model=ThreadListResponse,
    operation_id="list_threads",
)
async def list_threads(
    limit: int = Query(default=10, ge=1, le=100, description="取得する件数"),
) -> ThreadListResponse:
    """
    エージェントのスレッド一覧を取得する
    """
    logger.info(f"Listing threads with limit: {limit}")
    try:
        result = agent_repo.list_threads(limit=limit)
        logger.info(f"Retrieved {len(result.threads)} threads")
        return result
    except Exception as e:
        logger.error(f"Failed to list threads: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"スレッド一覧の取得に失敗しました: {str(e)}")
