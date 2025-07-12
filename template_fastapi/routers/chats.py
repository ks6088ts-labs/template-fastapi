from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates

from template_fastapi.repositories.chats import ChatRepository
from template_fastapi.settings.chats import get_chats_settings
from template_fastapi.settings.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="template_fastapi/templates")
chat_repository = ChatRepository()


@router.get(
    "/",
)
async def get(request: Request):
    """Get the chat page with configurable WebSocket URL."""
    logger.info("Serving chat page")
    settings = get_chats_settings()
    logger.debug(f"Using WebSocket URL: {settings.chats_websocket_url}")
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
    logger.info(f"WebSocket connection attempt for client {client_id}")
    try:
        await chat_repository.manager.connect(websocket)
        logger.info(f"WebSocket connected successfully for client {client_id}")
        
        while True:
            data = await websocket.receive_text()
            logger.debug(f"Received message from client {client_id}: {data[:100]}...")  # Log first 100 chars
            await chat_repository.handle_client_message(data, websocket, client_id)
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for client {client_id}")
        chat_repository.manager.disconnect(websocket)
        await chat_repository.handle_client_disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {str(e)}", exc_info=True)
        chat_repository.manager.disconnect(websocket)
