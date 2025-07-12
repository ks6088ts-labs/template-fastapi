from fastapi import APIRouter

from template_fastapi.routers.agents.azure_ai_foundry import router as azure_ai_foundry_router
from template_fastapi.routers.agents.langgraph import router as langgraph_router

router = APIRouter()

router.include_router(
    router=azure_ai_foundry_router,
    prefix="/azure-ai-foundry",
    responses={
        404: {
            "description": "Not found",
        },
    },
)

router.include_router(
    router=langgraph_router,
    prefix="/langgraph",
    responses={
        404: {
            "description": "Not found",
        },
    },
)
