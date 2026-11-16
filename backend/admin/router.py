"""Router agregat pentru modulele MVC administrative."""

from fastapi import APIRouter

from .content import router as content_router


admin_router = APIRouter()
admin_router.include_router(content_router)
