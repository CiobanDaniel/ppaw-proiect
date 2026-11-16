"""Dependențe, validări și răspunsuri comune pentru rutele MVC admin."""

from datetime import datetime
from decimal import Decimal
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from ..config import ADMIN_PREFIX, BASE_DIR
from ..crud import (
    AdminOperationError, AlerteAccessor, AnaliticeAccessor, CapitoleAccessor,
    CartiAccessor, CategoriiAccessor, CereriRetragereAccessor, ComentariiAccessor,
    EvenimenteAccessor, NiveleAccessor, NotificariAccessor, PlatiAccessor,
    RapoarteAccessor, RecenziiAccessor, SessionLocal, SetariAccessor,
    UtilizatoriAccessor,
)


templates = Jinja2Templates(directory=str(BASE_DIR / 'templates'))
VALID_ROLES = {'cititor', 'autor', 'admin'}
VALID_BOOK_STATES = {'ciorna', 'publicat'}
VALID_ALERT_TYPES = {'info', 'success', 'warning', 'danger'}
VALID_WITHDRAWAL_STATES = {'aprobata', 'respinsa'}
VALID_REPORT_STATES = {'rezolvat', 'respins'}


class AdminValidationError(Exception):
    """Eroare de domeniu care poate fi afișată administratorului."""


def redirect_with_feedback(url: str, key: str, message: str) -> RedirectResponse:
    if url.startswith('/') and not url.startswith(ADMIN_PREFIX):
        url = f'{ADMIN_PREFIX}{url}'
    separator = '&' if '?' in url else '?'
    return RedirectResponse(f'{url}{separator}{urlencode({key: message})}', status_code=303)


def return_to_form(request: Request, key: str, message: str) -> RedirectResponse:
    referer = request.headers.get('referer')
    if referer:
        parts = urlsplit(referer)
        if parts.path.startswith('/') and not parts.path.startswith('//'):
            query = dict(parse_qsl(parts.query, keep_blank_values=True))
            query[key] = message
            return RedirectResponse(urlunsplit(('', '', parts.path, urlencode(query), '')), status_code=303)
    return redirect_with_feedback(ADMIN_PREFIX, key, message)


def require_choice(value: str, allowed: set[str], label: str) -> str:
    if value not in allowed:
        raise AdminValidationError(f'Valoarea pentru {label} nu este validă.')
    return value


def require_non_negative(value: int | Decimal, label: str) -> int | Decimal:
    if value < 0:
        raise AdminValidationError(f'{label} nu poate fi negativ.')
    return value


def require_present(value: str, label: str) -> str:
    value = value.strip()
    if not value:
        raise AdminValidationError(f'{label} este obligatoriu.')
    return value


def get_or_404(entity, label: str):
    if entity is None:
        raise HTTPException(status_code=404, detail=f'{label} nu există sau a fost șters.')
    return entity


def parse_form_datetime(value: str, label: str) -> datetime:
    try:
        return datetime.strptime(value, '%Y-%m-%dT%H:%M')
    except ValueError as exc:
        raise AdminValidationError(f'{label} are un format invalid.') from exc


def accessor_dependency(accessor_type):
    def get_accessor():
        db = SessionLocal()
        try:
            yield accessor_type(db)
        finally:
            db.close()
    return get_accessor


get_users_accessor = accessor_dependency(UtilizatoriAccessor)
get_books_accessor = accessor_dependency(CartiAccessor)
get_categories_accessor = accessor_dependency(CategoriiAccessor)
get_settings_accessor = accessor_dependency(SetariAccessor)
get_alerts_accessor = accessor_dependency(AlerteAccessor)
get_chapters_accessor = accessor_dependency(CapitoleAccessor)
get_reviews_accessor = accessor_dependency(RecenziiAccessor)
get_comments_accessor = accessor_dependency(ComentariiAccessor)
get_levels_accessor = accessor_dependency(NiveleAccessor)
get_events_accessor = accessor_dependency(EvenimenteAccessor)
get_payments_accessor = accessor_dependency(PlatiAccessor)
get_withdrawals_accessor = accessor_dependency(CereriRetragereAccessor)
get_reports_accessor = accessor_dependency(RapoarteAccessor)
get_notifications_accessor = accessor_dependency(NotificariAccessor)
get_analytics_accessor = accessor_dependency(AnaliticeAccessor)


__all__ = ['AdminOperationError', 'AdminValidationError', 'VALID_ALERT_TYPES', 'VALID_BOOK_STATES',
           'VALID_REPORT_STATES', 'VALID_ROLES', 'VALID_WITHDRAWAL_STATES', 'get_alerts_accessor',
           'get_analytics_accessor', 'get_books_accessor', 'get_categories_accessor', 'get_chapters_accessor',
           'get_comments_accessor', 'get_events_accessor', 'get_levels_accessor', 'get_notifications_accessor',
           'get_or_404', 'get_payments_accessor', 'get_reports_accessor', 'get_reviews_accessor',
           'get_settings_accessor', 'get_users_accessor', 'get_withdrawals_accessor', 'parse_form_datetime',
           'redirect_with_feedback', 'require_choice', 'require_non_negative', 'require_present',
           'return_to_form', 'templates']
