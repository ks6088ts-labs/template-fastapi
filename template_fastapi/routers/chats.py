from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates

from template_fastapi.repositories.chats import ChatRepository
from template_fastapi.settings.chats import get_chats_settings

router = APIRouter()
templates = Jinja2Templates(directory="template_fastapi/templates")
chat_repository = ChatRepository()


@router.get(
    "/chats/",
    tags=["chats"],
)
async def get(request: Request):
    """Get the chat page with configurable WebSocket URL."""
    settings = get_chats_settings()
    return templates.TemplateResponse(
        "chats.html",
        {
            "request": request,
            "websocket_url": settings.chats_websocket_url,
        },
    )


@router.websocket(
    "/ws/{client_id}",
)
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    """WebSocket endpoint for chat functionality."""
    await chat_repository.manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await chat_repository.handle_client_message(data, websocket, client_id)
    except WebSocketDisconnect:
        chat_repository.manager.disconnect(websocket)
        await chat_repository.handle_client_disconnect(client_id)
