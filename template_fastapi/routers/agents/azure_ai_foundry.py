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
    try:
        return agent_repo.create_agent(request)
    except Exception as e:
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
    try:
        return agent_repo.get_agent(agent_id)
    except Exception as e:
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
    try:
        return agent_repo.list_agents(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"エージェント一覧の取得に失敗しました: {str(e)}")


@router.delete(
    "/{agent_id}",
    operation_id="delete_agent",
)
async def delete_agent(agent_id: str) -> dict:
    """
    エージェントを削除する
    """
    try:
        success = agent_repo.delete_agent(agent_id)
        if success:
            return {"message": "エージェントが正常に削除されました"}
        else:
            raise HTTPException(status_code=500, detail="エージェントの削除に失敗しました")
    except Exception as e:
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
    try:
        return agent_repo.chat_with_agent(agent_id, request)
    except Exception as e:
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
    try:
        return agent_repo.create_thread(request)
    except Exception as e:
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
    try:
        return agent_repo.get_thread(thread_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"スレッドが見つかりません: {str(e)}")


@router.delete(
    "/threads/{thread_id}",
    operation_id="delete_thread",
)
async def delete_thread(thread_id: str) -> dict:
    """
    スレッドを削除する
    """
    try:
        success = agent_repo.delete_thread(thread_id)
        if success:
            return {"message": "スレッドが正常に削除されました"}
        else:
            raise HTTPException(status_code=500, detail="スレッドの削除に失敗しました")
    except Exception as e:
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
    try:
        return agent_repo.list_threads(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"スレッド一覧の取得に失敗しました: {str(e)}")
