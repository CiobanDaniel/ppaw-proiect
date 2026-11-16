"""Dependențe reutilizabile pentru endpointurile API administrative."""

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

try:
    from .access_sessions import ACCESS_COOKIE_NAME, AccessSessionService
    from .api_dependencies import get_db
    from .models import Utilizatori
except ImportError:
    from access_sessions import ACCESS_COOKIE_NAME, AccessSessionService
    from api_dependencies import get_db
    from models import Utilizatori


def require_admin_api(request: Request, db: Session = Depends(get_db)) -> Utilizatori:
    sesiune = AccessSessionService(db).get_active_session(request.cookies.get(ACCESS_COOKIE_NAME))
    if not sesiune or not sesiune.id_utilizator:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Autentificare de administrator necesară.')
    administrator = db.query(Utilizatori).filter(
        Utilizatori.id == sesiune.id_utilizator,
        Utilizatori.rol == 'admin',
    ).first()
    if not administrator:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Contul nu are permisiuni de administrator.')
    return administrator
