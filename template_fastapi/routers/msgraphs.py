from fastapi import APIRouter

from template_fastapi.routers.msgraphs import sites

router = APIRouter()

# サブルーターを追加
router.include_router(sites.router, prefix="/sites", tags=["msgraphs/sites"])