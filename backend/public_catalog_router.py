"""Endpoint-uri publice pentru catalog și citirea capitolelor gratuite."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

try:
    from .access_sessions import ACCESS_COOKIE_NAME, AccessSessionService, set_access_cookie
    from .api_dependencies import get_db
    from .catalog_service import CapitolBlocatError, CatalogPublicService
except ImportError:
    from access_sessions import ACCESS_COOKIE_NAME, AccessSessionService, set_access_cookie
    from api_dependencies import get_db
    from catalog_service import CapitolBlocatError, CatalogPublicService


public_catalog_router = APIRouter(prefix='/api/v1', tags=['Catalog public'])


class CapitolCatalogSchema(BaseModel):
    id: int
    numar_capitol: int
    titlu: str
    este_gratuit: bool
    cost_puncte: int


class CarteCatalogSchema(BaseModel):
    id: int
    titlu: str
    descriere: Optional[str]
    url_imagine_coperta: Optional[str]
    autor: Optional[str]
    categorii: list[str]
    capitole: list[CapitolCatalogSchema] = []


class CapitolCitireSchema(BaseModel):
    id: int
    titlu: str
    numar_capitol: int
    continut: str


def serialize_carte(carte, include_capitole: bool = False) -> CarteCatalogSchema:
    capitole = []
    if include_capitole:
        capitole = [
            CapitolCatalogSchema(
                id=capitol.id,
                numar_capitol=capitol.numar_capitol,
                titlu=capitol.titlu,
                este_gratuit=bool(capitol.este_gratuit),
                cost_puncte=capitol.cost_puncte or 0,
            )
            for capitol in sorted(
                (capitol for capitol in carte.capitole if capitol.stare == 'publicat'),
                key=lambda capitol: capitol.numar_capitol,
            )
        ]
    return CarteCatalogSchema(
        id=carte.id,
        titlu=carte.titlu,
        descriere=carte.descriere,
        url_imagine_coperta=carte.url_imagine_coperta,
        autor=carte.utilizatori.nume_utilizator if carte.utilizatori else None,
        categorii=[categorie.nume for categorie in carte.categorii],
        capitole=capitole,
    )


def asigura_sesiune(request: Request, response: Response, db: Session):
    result = AccessSessionService(db).get_or_create_guest_session(request.cookies.get(ACCESS_COOKIE_NAME))
    if result.token_to_set:
        set_access_cookie(response, result.token_to_set)
    return result.session


@public_catalog_router.get('/carti', response_model=list[CarteCatalogSchema])
def get_carti_publice(db: Session = Depends(get_db)):
    return [serialize_carte(carte) for carte in CatalogPublicService(db).get_carti_publicate()]


@public_catalog_router.get('/carti/{carte_id}', response_model=CarteCatalogSchema)
def get_carte_publica(carte_id: int, db: Session = Depends(get_db)):
    carte = CatalogPublicService(db).get_carte_publicata(carte_id)
    if not carte:
        raise HTTPException(status_code=404, detail='Cartea publicată nu a fost găsită.')
    return serialize_carte(carte, include_capitole=True)


@public_catalog_router.get('/capitole/{capitol_id}/citire', response_model=CapitolCitireSchema)
def citeste_capitol_gratuit(
    capitol_id: int,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    service = CatalogPublicService(db)
    try:
        capitol = service.get_capitol_gratuit(capitol_id)
    except CapitolBlocatError as exc:
        raise HTTPException(status_code=403, detail='Capitolul necesită autentificare și acces eligibil.') from exc
    if not capitol:
        raise HTTPException(status_code=404, detail='Capitolul publicat nu a fost găsit.')
    sesiune = asigura_sesiune(request, response, db)
    service.inregistreaza_vizualizare(capitol, sesiune)
    return CapitolCitireSchema(
        id=capitol.id,
        titlu=capitol.titlu,
        numar_capitol=capitol.numar_capitol,
        continut=capitol.continut,
    )
