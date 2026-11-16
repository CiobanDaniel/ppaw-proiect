"""Documentația OpenAPI disponibilă numai în zona administrativă."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

try:
    from ..config import ADMIN_PREFIX
except ImportError:
    from config import ADMIN_PREFIX
from .common import templates


router = APIRouter()


@router.get('/docs', include_in_schema=False)
def api_docs(request: Request):
    return templates.TemplateResponse(
        request,
        'admin/api_docs.html',
        {'openapi_url': f'{ADMIN_PREFIX}/openapi.json'},
    )


@router.get('/openapi.json', include_in_schema=False)
def openapi_schema(request: Request):
    return JSONResponse(request.app.openapi())
