"""Punctul de intrare: platforma publică, zona admin și API-ul."""

from urllib.parse import urlencode

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError

from .access_sessions import ACCESS_COOKIE_NAME, AccessSessionService, clear_access_cookie, set_access_cookie
from .admin.common import AdminOperationError, AdminValidationError, return_to_form, templates
from .admin.router import admin_router
from .api_router import api_router
from .authentication import authenticate_admin
from .config import ADMIN_LEGACY_PREFIXES, ADMIN_PREFIX, FRONTEND_DIST_DIR
from .crud import SessionLocal
from .models import Utilizatori
from .public_catalog_router import public_catalog_router


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.include_router(api_router)
app.include_router(public_catalog_router)
app.include_router(admin_router)


def is_api_request(request: Request) -> bool:
    return request.url.path.startswith('/api')


def safe_admin_next(value: str | None) -> str:
    if value and value.startswith(ADMIN_PREFIX) and not value.startswith('//'):
        return value
    return ADMIN_PREFIX


@app.exception_handler(AdminValidationError)
async def admin_validation_error(request: Request, exc: AdminValidationError):
    return return_to_form(request, 'error', str(exc))


@app.exception_handler(AdminOperationError)
async def admin_operation_error(request: Request, exc: AdminOperationError):
    return return_to_form(request, 'error', str(exc))


@app.exception_handler(IntegrityError)
async def integrity_error(request: Request, exc: IntegrityError):
    if is_api_request(request):
        return JSONResponse({'detail': 'Datele încalcă o regulă de integritate.'}, status_code=409)
    return return_to_form(request, 'error', 'Datele încalcă o regulă de unicitate sau integritate. Verifică valorile introduse.')


@app.exception_handler(RequestValidationError)
async def request_validation_error(request: Request, exc: RequestValidationError):
    if is_api_request(request):
        return JSONResponse({'detail': exc.errors()}, status_code=422)
    return return_to_form(request, 'error', 'Datele formularului sunt incomplete sau au un format invalid.')


@app.exception_handler(HTTPException)
async def http_exception(request: Request, exc: HTTPException):
    if is_api_request(request):
        return JSONResponse({'detail': exc.detail}, status_code=exc.status_code)
    return templates.TemplateResponse(request, 'error.html', {'status_code': exc.status_code, 'message': exc.detail}, status_code=exc.status_code)


@app.middleware('http')
async def protect_admin_area(request: Request, call_next):
    path = request.url.path
    documentation_redirects = {'/docs': '/admin/docs', '/redoc': '/admin/docs', '/openapi.json': '/admin/openapi.json'}
    if path in documentation_redirects:
        return RedirectResponse(documentation_redirects[path], status_code=303)
    if path in ADMIN_LEGACY_PREFIXES or any(path.startswith(f'{prefix}/') for prefix in ADMIN_LEGACY_PREFIXES):
        query = f'?{request.url.query}' if request.url.query else ''
        return RedirectResponse(f'{ADMIN_PREFIX}{path}{query}', status_code=303 if request.method in {'GET', 'HEAD'} else 307)
    if not path.startswith(ADMIN_PREFIX):
        return await call_next(request)
    if path in {f'{ADMIN_PREFIX}/login', f'{ADMIN_PREFIX}/logout'}:
        return await call_next(request)

    db = SessionLocal()
    try:
        session = AccessSessionService(db).get_active_session(request.cookies.get(ACCESS_COOKIE_NAME))
        administrator = db.query(Utilizatori).filter(
            Utilizatori.id == session.id_utilizator, Utilizatori.rol == 'admin'
        ).first() if session and session.id_utilizator else None
        if not administrator:
            destination = f'{ADMIN_PREFIX}{path[len(ADMIN_PREFIX):]}'
            return RedirectResponse(f'{ADMIN_PREFIX}/login?{urlencode({"next": destination})}', status_code=303)
    finally:
        db.close()

    request.scope['path'] = path[len(ADMIN_PREFIX):] or '/'
    request.scope['raw_path'] = request.scope['path'].encode('utf-8')
    request.state.is_admin_route = True
    return await call_next(request)


@app.get(f'{ADMIN_PREFIX}/login')
def admin_login_get(request: Request, next: str | None = None):
    return templates.TemplateResponse(request, 'admin/login.html', {'next': safe_admin_next(next)})


@app.post(f'{ADMIN_PREFIX}/login')
def admin_login_post(request: Request, identificator: str = Form(...), parola: str = Form(...), next: str | None = Form(None)):
    db = SessionLocal()
    try:
        administrator = authenticate_admin(db, identificator, parola)
        if not administrator:
            return RedirectResponse(f'{ADMIN_PREFIX}/login?error=Date+de+autentificare+invalide.', status_code=303)
        result = AccessSessionService(db).get_or_create_guest_session(request.cookies.get(ACCESS_COOKIE_NAME))
        AccessSessionService(db).associate_user(result.session, administrator.id)
    finally:
        db.close()
    response = RedirectResponse(safe_admin_next(next), status_code=303)
    if result.token_to_set:
        set_access_cookie(response, result.token_to_set)
    return response


@app.post(f'{ADMIN_PREFIX}/logout')
def admin_logout(request: Request):
    db = SessionLocal()
    try:
        AccessSessionService(db).revoke_session(request.cookies.get(ACCESS_COOKIE_NAME))
    finally:
        db.close()
    response = RedirectResponse('/', status_code=303)
    clear_access_cookie(response)
    return response


@app.get('/')
def home(request: Request):
    if getattr(request.state, 'is_admin_route', False):
        return templates.TemplateResponse(request, 'admin/dashboard/home.html', {})
    index_file = FRONTEND_DIST_DIR / 'index.html'
    if not index_file.exists():
        return PlainTextResponse('Frontendul nu este compilat. Rulează `npm run build` în directorul frontend.', status_code=503)
    return FileResponse(index_file)


app.mount('/assets', StaticFiles(directory=str(FRONTEND_DIST_DIR / 'assets'), check_dir=False), name='frontend-assets')


@app.get('/{frontend_path:path}', include_in_schema=False)
def frontend_fallback():
    index_file = FRONTEND_DIST_DIR / 'index.html'
    if not index_file.exists():
        return PlainTextResponse('Frontendul nu este compilat. Rulează `npm run build` în directorul frontend.', status_code=503)
    return FileResponse(index_file)
