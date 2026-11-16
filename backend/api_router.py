from datetime import datetime
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Importă SessionLocal și accessors din crud
try:
    from .crud import CategoriiAccessor # sau alte entități dorite
    from .access_sessions import ACCESS_COOKIE_NAME, AccessSessionService, set_access_cookie
    from .api_dependencies import get_db
except ImportError:
    from crud import CategoriiAccessor
    from access_sessions import ACCESS_COOKIE_NAME, AccessSessionService, set_access_cookie
    from api_dependencies import get_db

api_router = APIRouter(prefix="/api", tags=["API Lab 7"])

# --- EXERCIȚIUL 2: Modele/DTO-uri separate (Scheme Pydantic) ---
class CategorieCreateUpdateSchema(BaseModel):
    nume: str
    descriere: Optional[str] = None

class CategorieResponseSchema(BaseModel):
    id: int
    nume: str
    descriere: Optional[str] = None

    class Config:
        from_attributes = True  # Asigură maparea automată din obiectele SQLAlchemy (ORM)


class SesiuneAccesResponseSchema(BaseModel):
    tip_sesiune: Literal['guest', 'autentificata']
    autentificat: bool
    expira_la: Optional[datetime] = None


@api_router.get('/sesiune', response_model=SesiuneAccesResponseSchema)
def get_sau_creeaza_sesiune(request: Request, response: Response, db: Session = Depends(get_db)):
    """Asigură o sesiune guest fără a crea un cont de utilizator."""
    result = AccessSessionService(db).get_or_create_guest_session(request.cookies.get(ACCESS_COOKIE_NAME))
    session = result.session
    if result.token_to_set:
        set_access_cookie(response, result.token_to_set)
    autentificat = session.id_utilizator is not None
    return SesiuneAccesResponseSchema(
        tip_sesiune='autentificata' if autentificat else 'guest',
        autentificat=autentificat,
        expira_la=session.expira_la,
    )


# --- EXERCIȚIUL 1: Endpoint-uri GET și GET(int id) ---
@api_router.get("/categorii", response_model=List[CategorieResponseSchema])
def get_toate_categorii_api(db: Session = Depends(get_db)):
    accessor = CategoriiAccessor(db)
    return accessor.get_toate_categoriile()

@api_router.get("/categorii/{cat_id}", response_model=CategorieResponseSchema)
def get_categorie_id_api(cat_id: int, db: Session = Depends(get_db)):
    accessor = CategoriiAccessor(db)
    categorie = accessor.get_categorie_by_id(cat_id)
    if not categorie:
        raise HTTPException(status_code=404, detail="Categoria nu a fost găsită.")
    return categorie


# --- EXERCIȚIUL 3: Endpoint-uri POST și PUT (preiau date din Body) ---
@api_router.post("/categorii", response_model=CategorieResponseSchema, status_code=status.HTTP_201_CREATED)
def create_categorie_api(payload: CategorieCreateUpdateSchema, db: Session = Depends(get_db)):
    accessor = CategoriiAccessor(db)
    noua_cat = accessor.add_categorie(nume=payload.nume, descriere=payload.descriere)
    return noua_cat

@api_router.put("/categorii/{cat_id}", response_model=CategorieResponseSchema)
def update_categorie_api(cat_id: int, payload: CategorieCreateUpdateSchema, db: Session = Depends(get_db)):
    accessor = CategoriiAccessor(db)
    actualizata = accessor.update_categorie(cat_id=cat_id, nume=payload.nume, descriere=payload.descriere)
    if not actualizata:
        raise HTTPException(status_code=404, detail="Categoria nu a fost găsită.")
    return actualizata
