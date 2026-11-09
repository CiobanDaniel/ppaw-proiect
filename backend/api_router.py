from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

# Importă SessionLocal și accessors din crud
try:
    from .crud import SessionLocal, CategoriiAccessor # sau alte entități dorite
except ImportError:
    from crud import SessionLocal, CategoriiAccessor

api_router = APIRouter(prefix="/api", tags=["API Lab 7"])

# Dependență pentru sesiune de BDD în API
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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