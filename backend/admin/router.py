"""Router agregat pentru modulele MVC administrative."""

from fastapi import APIRouter

from .content import router as content_router
from .community import router as community_router
from .finance import router as finance_router
from .operations import router as operations_router
from .docs import router as docs_router


admin_router = APIRouter()
admin_router.include_router(content_router)
admin_router.include_router(community_router)
admin_router.include_router(finance_router)
admin_router.include_router(operations_router)
admin_router.include_router(docs_router)
