import datetime
import os
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
try:
    from .models import Utilizatori, Carti
    from . import models as _models
    import sys
    sys.modules.setdefault("models", _models)
except ImportError:
    from models import Utilizatori, Carti

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:3903@localhost:5432/proiect_codefirst")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class AdminOperationError(Exception):
    """Operație administrativă respinsă dintr-o regulă de domeniu."""


def commit_or_raise(db_session, message: str = "Nu s-a putut salva modificarea. Verifică datele introduse."):
    try:
        db_session.commit()
    except IntegrityError as exc:
        db_session.rollback()
        raise AdminOperationError(message) from exc

class UtilizatoriAccessor:
    def __init__(self, db_session):
        self.db = db_session

    def get_all_users(self):
        return self.db.query(Utilizatori).all()

    def get_user_by_id(self, user_id: int):
        # Returnează un singur utilizator pentru acțiunile Details și Edit (GET)
        from models import Utilizatori
        return self.db.query(Utilizatori).filter(Utilizatori.id == user_id).first()

    def add_entity(self, nume_utilizator: str, email: str, parola_hash: str, rol: str, telefon: str, adresa: str, data_nasterii):
        # Echivalentul AddEntity pentru acțiunea Create (POST)
        from models import Utilizatori
        nou_utilizator = Utilizatori(
            nume_utilizator=nume_utilizator,
            email=email,
            parola_hash=parola_hash,
            rol=rol,
            telefon=telefon,
            adresa=adresa,
            data_nasterii=data_nasterii
        )
        self.db.add(nou_utilizator)
        self.db.commit()
        self.db.refresh(nou_utilizator)
        return nou_utilizator

    def update_entity(self, user_id: int, nume_utilizator: str, email: str, rol: str, telefon: str, adresa: str, data_nasterii):
        # Echivalentul UpdateEntity pentru acțiunea Edit (POST)
        utilizator = self.get_user_by_id(user_id)
        if utilizator:
            utilizator.nume_utilizator = nume_utilizator
            utilizator.email = email
            utilizator.rol = rol
            utilizator.telefon = telefon
            utilizator.adresa = adresa
            utilizator.data_nasterii = data_nasterii
            
            self.db.commit()
            self.db.refresh(utilizator)
        return utilizator

class CartiAccessor:
    def __init__(self, db_session):
        self.db = db_session

    def get_books_by_author(self, author_id):
        # Aici folosim relatia prin cheia straina (id_autor)
        return self.db.query(Carti).filter(Carti.id_autor == author_id).all()

class CartiAccessor:
    def __init__(self, db_session):
        self.db = db_session

    def get_books_by_author(self, author_id):
        # Aici folosim relatia prin cheia straina (id_autor)
        from models import Carti
        return self.db.query(Carti).filter(Carti.id_autor == author_id).all()

    def get_all_carti(self):
        # Extrage toate cărțile pentru Index
        from models import Carti
        return self.db.query(Carti).all()

    def get_autori_pentru_dropdown(self):
        # Extrage utilizatorii pentru formularul de Create
        from models import Utilizatori
        return self.db.query(Utilizatori).filter(Utilizatori.rol == 'autor').order_by(Utilizatori.nume_utilizator).all()

    def add_carte(self, titlu: str, id_autor: int, descriere: str, stare: str):
        # Salvează o carte nouă legată de un autor existent
        from models import Carti
        autor = self.db.query(Utilizatori).filter(Utilizatori.id == id_autor, Utilizatori.rol == 'autor').first()
        if not autor:
            raise AdminOperationError("Selectează un utilizator cu rolul «autor».")
        noua_carte = Carti(
            titlu=titlu,
            id_autor=id_autor,
            descriere=descriere,
            stare=stare
        )
        self.db.add(noua_carte)
        commit_or_raise(self.db, "Cartea nu a putut fi salvată. Verifică datele introduse.")

    def get_carte_by_id(self, carte_id: int):
        from models import Carti
        return self.db.query(Carti).filter(Carti.id == carte_id).first()

    def update_carte(self, carte_id: int, titlu: str, id_autor: int, descriere: str, stare: str):
        carte = self.get_carte_by_id(carte_id)
        if carte:
            autor = self.db.query(Utilizatori).filter(Utilizatori.id == id_autor, Utilizatori.rol == 'autor').first()
            if not autor:
                raise AdminOperationError("Selectează un utilizator cu rolul «autor».")
            carte.titlu = titlu
            carte.id_autor = id_autor
            carte.descriere = descriere
            carte.stare = stare
            commit_or_raise(self.db, "Cartea nu a putut fi actualizată. Verifică datele introduse.")
            self.db.refresh(carte)
        return carte
class CategoriiAccessor:
    def __init__(self, db_session):
        self.db = db_session

    def get_toate_categoriile(self):
        from models import Categorii
        return self.db.query(Categorii).order_by(Categorii.nume).all()

    def get_categorie_by_id(self, cat_id: int):
        from models import Categorii
        return self.db.query(Categorii).filter(Categorii.id == cat_id).first()

    def add_categorie(self, nume: str, descriere: str = None):
        from models import Categorii
        noua_cat = Categorii(nume=nume, descriere=descriere)
        self.db.add(noua_cat)
        self.db.commit()
        self.db.refresh(noua_cat)
        return noua_cat

    def update_categorie(self, cat_id: int, nume: str, descriere: str = None):
        categorie = self.get_categorie_by_id(cat_id)
        if categorie:
            categorie.nume = nume
            categorie.descriere = descriere
            self.db.commit()
            self.db.refresh(categorie)
        return categorie

class SetariAccessor:
    def __init__(self, db_session):
        self.db = db_session

    def get_toate_setarile(self):
        from models import SetariPlatforma
        return self.db.query(SetariPlatforma).order_by(SetariPlatforma.nume_setare).all()

    def get_setare_by_id(self, setare_id: int):
        from models import SetariPlatforma
        return self.db.query(SetariPlatforma).filter(SetariPlatforma.id == setare_id).first()

    def add_setare(self, nume: str, valoare: str):
        from models import SetariPlatforma
        noua_setare = SetariPlatforma(nume_setare=nume, valoare_setare=valoare)
        self.db.add(noua_setare)
        self.db.commit()
        return noua_setare

    def update_setare(self, setare_id: int, nume: str, valoare: str):
        setare = self.get_setare_by_id(setare_id)
        if setare:
            setare.nume_setare = nume
            setare.valoare_setare = valoare
            setare.data_actualizarii = datetime.datetime.now()
            self.db.commit()
            self.db.refresh(setare)
        return setare

class AlerteAccessor:
    def __init__(self, db_session):
        self.db = db_session

    def get_toate_alertele(self):
        from models import AlerteSistem
        # Le sortăm descrescător după ID / data creării pentru a vedea noutățile primele
        return self.db.query(AlerteSistem).order_by(AlerteSistem.id.desc()).all()

    def get_alerta_by_id(self, alerta_id: int):
        from models import AlerteSistem
        return self.db.query(AlerteSistem).filter(AlerteSistem.id == alerta_id).first()

    def add_alerta(self, mesaj: str, tip_alerta: str = 'info'):
        from models import AlerteSistem
        noua_alerta = AlerteSistem(mesaj=mesaj, tip_alerta=tip_alerta)
        self.db.add(noua_alerta)
        self.db.commit()
        return noua_alerta

    def update_alerta(self, alerta_id: int, mesaj: str, tip_alerta: str):
        alerta = self.get_alerta_by_id(alerta_id)
        if alerta:
            alerta.mesaj = mesaj
            alerta.tip_alerta = tip_alerta
            self.db.commit()
            self.db.refresh(alerta)
        return alerta

class CapitoleAccessor:
    def __init__(self, db_session):
        self.db = db_session

    def get_toate_capitolele(self):
        from models import Capitole
        # Sortăm după carte și apoi după numărul capitolului pentru o afișare logică
        return self.db.query(Capitole).order_by(Capitole.id_carte, Capitole.numar_capitol).all()

    def get_capitol_by_id(self, cap_id: int):
        from models import Capitole
        return self.db.query(Capitole).filter(Capitole.id == cap_id).first()

    def get_carti_pentru_dropdown(self):
        from models import Carti
        return self.db.query(Carti).order_by(Carti.titlu).all()

    def add_capitol(self, id_carte: int, numar_capitol: int, titlu: str, continut: str, este_gratuit: bool, cost_puncte: int, stare: str):
        from models import Capitole
        nou_capitol = Capitole(
            id_carte=id_carte,
            numar_capitol=numar_capitol,
            titlu=titlu,
            continut=continut,
            este_gratuit=este_gratuit,
            cost_puncte=cost_puncte,
            stare=stare
        )
        self.db.add(nou_capitol)
        self.db.commit()
        return nou_capitol

    def update_capitol(self, cap_id: int, id_carte: int, numar_capitol: int, titlu: str, continut: str, este_gratuit: bool, cost_puncte: int, stare: str):
        capitol = self.get_capitol_by_id(cap_id)
        if capitol:
            capitol.id_carte = id_carte
            capitol.numar_capitol = numar_capitol
            capitol.titlu = titlu
            capitol.continut = continut
            capitol.este_gratuit = este_gratuit
            capitol.cost_puncte = cost_puncte
            capitol.stare = stare
            self.db.commit()
            self.db.refresh(capitol)
        return capitol

class RecenziiAccessor:
    def __init__(self, db_session):
        self.db = db_session

    def get_toate_recenziile(self):
        from models import Recenzii
        # Sortăm descrescător pentru a vedea cele mai noi recenzii primele
        return self.db.query(Recenzii).order_by(Recenzii.id.desc()).all()

    def get_recenzie_by_id(self, rec_id: int):
        from models import Recenzii
        return self.db.query(Recenzii).filter(Recenzii.id == rec_id).first()

    def update_recenzie(self, rec_id: int, nota: int, text_comentariu: str):
        # Adminul poate ajusta nota sau cenzura textul comentariului
        recenzie = self.get_recenzie_by_id(rec_id)
        if recenzie:
            recenzie.nota = nota
            recenzie.text_comentariu = text_comentariu
            self.db.commit()
            self.db.refresh(recenzie)
        return recenzie

class ComentariiAccessor:
    def __init__(self, db_session):
        self.db = db_session

    def get_toate_comentariile(self):
        from models import Comentarii
        # Le sortăm descrescător pentru a vedea comentariile noi primele
        return self.db.query(Comentarii).order_by(Comentarii.id.desc()).all()

    def get_comentariu_by_id(self, com_id: int):
        from models import Comentarii
        return self.db.query(Comentarii).filter(Comentarii.id == com_id).first()

    def update_comentariu(self, com_id: int, continut: str):
        # Adminul poate edita/cenzura doar textul
        comentariu = self.get_comentariu_by_id(com_id)
        if comentariu:
            comentariu.continut = continut
            self.db.commit()
            self.db.refresh(comentariu)
        return comentariu

class NiveleAccessor:
    def __init__(self, db_session):
        self.db = db_session

    def get_toate_nivelele(self):
        from models import NiveleAbonament
        return self.db.query(NiveleAbonament).order_by(NiveleAbonament.pret_real).all()

    def get_nivel_by_id(self, nivel_id: int):
        from models import NiveleAbonament
        return self.db.query(NiveleAbonament).filter(NiveleAbonament.id == nivel_id).first()

    def add_nivel(self, nume: str, pret_real: float, descriere_beneficii: str):
        from models import NiveleAbonament
        nou_nivel = NiveleAbonament(nume=nume, pret_real=pret_real, descriere_beneficii=descriere_beneficii)
        self.db.add(nou_nivel)
        self.db.commit()
        return nou_nivel

    def update_nivel(self, nivel_id: int, nume: str, pret_real: float, descriere_beneficii: str):
        nivel = self.get_nivel_by_id(nivel_id)
        if nivel:
            nivel.nume = nume
            nivel.pret_real = pret_real
            nivel.descriere_beneficii = descriere_beneficii
            self.db.commit()
            self.db.refresh(nivel)
        return nivel

class EvenimenteAccessor:
    def __init__(self, db_session):
        self.db = db_session

    def get_toate_evenimentele(self):
        from models import EvenimentePromotionale
        return self.db.query(EvenimentePromotionale).order_by(EvenimentePromotionale.data_inceput.desc()).all()

    def get_eveniment_by_id(self, ev_id: int):
        from models import EvenimentePromotionale
        return self.db.query(EvenimentePromotionale).filter(EvenimentePromotionale.id == ev_id).first()

    def add_eveniment(self, nume: str, recompensa_puncte: int, data_inceput, data_sfarsit, este_activ: bool):
        from models import EvenimentePromotionale
        nou_ev = EvenimentePromotionale(nume=nume, recompensa_puncte=recompensa_puncte, data_inceput=data_inceput, data_sfarsit=data_sfarsit, este_activ=este_activ)
        self.db.add(nou_ev)
        self.db.commit()
        return nou_ev

    def update_eveniment(self, ev_id: int, nume: str, recompensa_puncte: int, data_inceput, data_sfarsit, este_activ: bool):
        ev = self.get_eveniment_by_id(ev_id)
        if ev:
            ev.nume = nume
            ev.recompensa_puncte = recompensa_puncte
            ev.data_inceput = data_inceput
            ev.data_sfarsit = data_sfarsit
            ev.este_activ = este_activ
            self.db.commit()
            self.db.refresh(ev)
        return ev

class PlatiAccessor:
    def __init__(self, db_session):
        self.db = db_session

    def get_toate_platile(self):
        from models import Plati
        # Sortăm descrescător după data creării pentru a vedea cele mai recente tranzacții
        return self.db.query(Plati).order_by(Plati.data_crearii.desc()).all()

    def get_plata_by_id(self, plata_id: int):
        from models import Plati
        return self.db.query(Plati).filter(Plati.id == plata_id).first()

    def get_admini(self):
        from models import Utilizatori
        return self.db.query(Utilizatori).filter(Utilizatori.rol == 'admin').order_by(Utilizatori.nume_utilizator).all()

    def anuleaza_plata_si_servicii(self, plata_id: int, id_admin: int, motiv: str):
        """Rambursare demonstrativă atomică, cu audit și fără rată de conversie inventată."""
        from models import Plati, IstoricAbonamente, TranzactiiPuncte, Utilizatori

        admin = self.db.query(Utilizatori).filter(Utilizatori.id == id_admin, Utilizatori.rol == 'admin').first()
        if not admin:
            raise AdminOperationError("Selectează un administrator valid pentru rambursare.")

        plata = self.db.query(Plati).filter(Plati.id == plata_id).with_for_update().first()
        if not plata:
            return None
        if plata.stare != 'finalizat':
            raise AdminOperationError("Doar o plată finalizată poate fi rambursată o singură dată.")

        tranzactie_puncte = None
        utilizator = None
        if plata.scop_plata == 'achizitie_puncte':
            tranzactie_initiala = self.db.query(TranzactiiPuncte).filter(
                TranzactiiPuncte.id_utilizator == plata.id_utilizator,
                TranzactiiPuncte.tip_referinta == 'plata',
                TranzactiiPuncte.id_referinta == plata.id,
                TranzactiiPuncte.valoare > 0,
            ).first()
            if not tranzactie_initiala:
                raise AdminOperationError("Plata nu are o achiziție de puncte asociată; rambursarea nu poate fi calculată sigur.")
            utilizator = self.db.query(Utilizatori).filter(Utilizatori.id == plata.id_utilizator).with_for_update().first()
            if not utilizator or (utilizator.puncte or 0) < tranzactie_initiala.valoare:
                raise AdminOperationError("Utilizatorul nu mai are suficiente puncte pentru această rambursare simulată.")
            tranzactie_puncte = TranzactiiPuncte(
                valoare=-tranzactie_initiala.valoare,
                tip_tranzactie='retragere',
                motiv=f'Rambursare simulată plată #{plata.id}',
                id_utilizator=plata.id_utilizator,
                tip_referinta='rambursare_plata',
                id_referinta=plata.id,
            )

        plata.stare = 'rambursat'
        plata.id_admin_rambursare = admin.id
        plata.motiv_rambursare = motiv
        plata.data_rambursarii = datetime.datetime.now(datetime.UTC)
        abonament = self.db.query(IstoricAbonamente).filter(
            IstoricAbonamente.id_plata == plata.id, IstoricAbonamente.stare == 'activ'
        ).with_for_update().first()
        if abonament:
            abonament.stare = 'anulat'
            abonament.data_sfarsit = datetime.datetime.now(datetime.UTC)
        if tranzactie_puncte:
            utilizator.puncte -= tranzactie_initiala.valoare
            self.db.add(tranzactie_puncte)
        commit_or_raise(self.db, "Rambursarea nu a putut fi salvată.")
        return plata

class CereriRetragereAccessor:
    def __init__(self, db_session):
        self.db = db_session

    def get_toate_cererile(self):
        from models import CereriRetragere
        return self.db.query(CereriRetragere).order_by(CereriRetragere.data_crearii.desc()).all()

    def get_cerere_by_id(self, cerere_id: int):
        from models import CereriRetragere
        return self.db.query(CereriRetragere).filter(CereriRetragere.id == cerere_id).first()

    def get_admini(self):
        from models import Utilizatori
        return self.db.query(Utilizatori).filter(Utilizatori.rol == 'admin').order_by(Utilizatori.nume_utilizator).all()

    def proceseaza_cerere(self, cerere_id: int, noua_stare: str, id_admin_procesare: int, observatii: str | None):
        from models import CereriRetragere, Utilizatori
        if noua_stare not in {'aprobata', 'respinsa'}:
            raise AdminOperationError("Starea cererii de retragere nu este validă.")
        admin = self.db.query(Utilizatori).filter(Utilizatori.id == id_admin_procesare, Utilizatori.rol == 'admin').first()
        if not admin:
            raise AdminOperationError("Selectează un administrator valid pentru procesare.")
        cerere = self.db.query(CereriRetragere).filter(CereriRetragere.id == cerere_id).with_for_update().first()
        if not cerere:
            return None
        if cerere.stare != 'in_asteptare':
            raise AdminOperationError("Această cerere a fost deja procesată și nu mai poate fi modificată.")
        cerere.stare = noua_stare
        cerere.data_procesarii = datetime.datetime.now(datetime.UTC)
        cerere.id_admin_procesare = admin.id
        cerere.observatii_procesare = observatii.strip() if observatii else None
        commit_or_raise(self.db, "Cererea de retragere nu a putut fi procesată.")
        self.db.refresh(cerere)
        return cerere

class RapoarteAccessor:
    def __init__(self, db_session):
        self.db = db_session

    def get_toate_rapoartele(self):
        from models import RapoarteContinut
        # Le sortăm descrescător, ca rapoartele noi să fie primele
        return self.db.query(RapoarteContinut).order_by(RapoarteContinut.stare, RapoarteContinut.data_crearii.desc()).all()

    def get_raport_by_id(self, rap_id: int):
        from models import RapoarteContinut
        return self.db.query(RapoarteContinut).filter(RapoarteContinut.id == rap_id).first()

    def get_admini(self):
        from models import Utilizatori
        # Returnăm doar utilizatorii care au rolul de 'admin' pentru a-i asocia ca rezolvitori
        return self.db.query(Utilizatori).filter(Utilizatori.rol == 'admin').all()

    def rezolva_raport(self, rap_id: int, stare: str, id_admin_rezolvare: int):
        from models import Utilizatori
        admin = self.db.query(Utilizatori).filter(Utilizatori.id == id_admin_rezolvare, Utilizatori.rol == 'admin').first()
        if not admin:
            raise AdminOperationError("Selectează un administrator valid pentru soluționare.")
        raport = self.get_raport_by_id(rap_id)
        if raport:
            if raport.stare != 'deschis':
                raise AdminOperationError("Acest raport a fost deja închis.")
            raport.stare = stare
            raport.id_admin_rezolvare = id_admin_rezolvare
            commit_or_raise(self.db, "Raportul nu a putut fi actualizat.")
            self.db.refresh(raport)
        return raport

class NotificariAccessor:
    def __init__(self, db_session):
        self.db = db_session

    def get_toate_notificarile(self):
        from models import Notificari
        return self.db.query(Notificari).order_by(Notificari.data_crearii.desc()).all()

    def get_utilizatori(self):
        from models import Utilizatori
        return self.db.query(Utilizatori).order_by(Utilizatori.nume_utilizator).all()

    def add_notificare(self, id_utilizator: int, titlu: str, mesaj: str):
        from models import Notificari
        noua_notificare = Notificari(id_utilizator=id_utilizator, titlu=titlu, mesaj=mesaj)
        self.db.add(noua_notificare)
        self.db.commit()
        return noua_notificare

class AnaliticeAccessor:
    def __init__(self, db_session):
        self.db = db_session

    def get_istoric_abonamente(self):
        from models import IstoricAbonamente
        return self.db.query(IstoricAbonamente).order_by(IstoricAbonamente.data_inceput.desc()).all()

    def get_tranzactii_puncte(self):
        from models import TranzactiiPuncte
        return self.db.query(TranzactiiPuncte).order_by(TranzactiiPuncte.data_crearii.desc()).all()

    def get_vizualizari(self):
        from models import VizualizariCapitole
        return self.db.query(VizualizariCapitole).order_by(VizualizariCapitole.data_vizualizarii.desc()).limit(200).all()


