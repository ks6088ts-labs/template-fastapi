
from fastapi import APIRouter, HTTPException, Query

from template_fastapi.models.agent import (
    AgentListResponse,
    AgentRequest,
    AgentResponse,
    ChatRequest,
    ChatResponse,
)
from template_fastapi.repositories.agents import AgentRepository

router = APIRouter()
agent_repo = AgentRepository()


@router.post(
    "/agents/",
    response_model=AgentResponse,
    tags=["agents"],
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
    "/agents/{agent_id}",
    response_model=AgentResponse,
    tags=["agents"],
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
    "/agents/",
    response_model=AgentListResponse,
    tags=["agents"],
    operation_id="list_agents",
)
async def list_agents(
    limit: int = Query(default=10, ge=1, le=100, description="取得する件数"),
    offset: int = Query(default=0, ge=0, description="オフセット"),
) -> AgentListResponse:
    """
    エージェントの一覧を取得する
    """
    try:
        return agent_repo.list_agents(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"エージェント一覧の取得に失敗しました: {str(e)}")


@router.delete(
    "/agents/{agent_id}",
    tags=["agents"],
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
    "/agents/{agent_id}/chat",
    response_model=ChatResponse,
    tags=["agents"],
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
