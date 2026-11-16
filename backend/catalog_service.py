"""Reguli de acces pentru catalogul public și reader-ul guest."""

from sqlalchemy.orm import Session, joinedload, selectinload

try:
    from .models import Capitole, Carti, SesiuniAcces, VizualizariCapitole
except ImportError:
    from models import Capitole, Carti, SesiuniAcces, VizualizariCapitole


class CapitolBlocatError(Exception):
    pass


class CatalogPublicService:
    def __init__(self, db: Session):
        self.db = db

    def get_carti_publicate(self) -> list[Carti]:
        return self.db.query(Carti).options(
            joinedload(Carti.utilizatori),
            selectinload(Carti.categorii),
        ).filter(Carti.stare == 'publicat').order_by(Carti.data_crearii.desc()).all()

    def get_carte_publicata(self, carte_id: int) -> Carti | None:
        return self.db.query(Carti).options(
            joinedload(Carti.utilizatori),
            selectinload(Carti.categorii),
            selectinload(Carti.capitole),
        ).filter(Carti.id == carte_id, Carti.stare == 'publicat').first()

    def get_capitol_gratuit(self, capitol_id: int) -> Capitole | None:
        capitol = self.db.query(Capitole).options(joinedload(Capitole.carti)).join(Carti).filter(
            Capitole.id == capitol_id,
            Capitole.stare == 'publicat',
            Carti.stare == 'publicat',
        ).first()
        if capitol and not capitol.este_gratuit:
            raise CapitolBlocatError
        return capitol

    def inregistreaza_vizualizare(self, capitol: Capitole, sesiune: SesiuniAcces) -> None:
        self.db.add(VizualizariCapitole(
            id_capitol=capitol.id,
            id_utilizator=sesiune.id_utilizator,
            id_sesiune_acces=sesiune.id,
        ))
        self.db.commit()
