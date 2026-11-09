from decimal import Decimal
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import List
try:  # Permite atât `uvicorn backend.main:app`, cât și rularea din directorul backend.
    from .crud import SessionLocal, UtilizatoriAccessor, CartiAccessor, CategoriiAccessor, SetariAccessor, AlerteAccessor, CapitoleAccessor, RecenziiAccessor, ComentariiAccessor, NiveleAccessor, EvenimenteAccessor, PlatiAccessor, CereriRetragereAccessor, RapoarteAccessor, NotificariAccessor, AnaliticeAccessor, AdminOperationError
except ImportError:
    from crud import SessionLocal, UtilizatoriAccessor, CartiAccessor, CategoriiAccessor, SetariAccessor, AlerteAccessor, CapitoleAccessor, RecenziiAccessor, ComentariiAccessor, NiveleAccessor, EvenimenteAccessor, PlatiAccessor, CereriRetragereAccessor, RapoarteAccessor, NotificariAccessor, AnaliticeAccessor, AdminOperationError

app = FastAPI()

try:
    from .api_router import api_router
except ImportError:
    from api_router import api_router

app.include_router(api_router)

BASE_DIR = Path(__file__).resolve().parent
VALID_ROLES = {"cititor", "autor", "admin"}
VALID_BOOK_STATES = {"ciorna", "publicat"}
VALID_ALERT_TYPES = {"info", "success", "warning", "danger"}
VALID_WITHDRAWAL_STATES = {"aprobata", "respinsa"}
VALID_REPORT_STATES = {"rezolvat", "respins"}


class AdminValidationError(Exception):
    """Eroare de domeniu care poate fi afișată administratorului."""


def redirect_with_feedback(url: str, key: str, message: str) -> RedirectResponse:
    separator = "&" if "?" in url else "?"
    return RedirectResponse(url=f"{url}{separator}{urlencode({key: message})}", status_code=303)


def return_to_form(request: Request, key: str, message: str) -> RedirectResponse:
    """Întoarce administratorul la formular fără a avea încredere în host-ul din Referer."""
    referer = request.headers.get("referer")
    if referer:
        parts = urlsplit(referer)
        if parts.path.startswith("/") and not parts.path.startswith("//"):
            query = dict(parse_qsl(parts.query, keep_blank_values=True))
            query[key] = message
            return RedirectResponse(urlunsplit(("", "", parts.path, urlencode(query), "")), status_code=303)
    return redirect_with_feedback("/", key, message)


def require_choice(value: str, allowed: set[str], label: str) -> str:
    if value not in allowed:
        raise AdminValidationError(f"Valoarea pentru {label} nu este validă.")
    return value


def require_non_negative(value: int | Decimal, label: str) -> int | Decimal:
    if value < 0:
        raise AdminValidationError(f"{label} nu poate fi negativ.")
    return value


def require_present(value: str, label: str) -> str:
    value = value.strip()
    if not value:
        raise AdminValidationError(f"{label} este obligatoriu.")
    return value


def get_or_404(entity, label: str):
    if entity is None:
        raise HTTPException(status_code=404, detail=f"{label} nu există sau a fost șters.")
    return entity


def parse_form_datetime(value: str, label: str) -> datetime:
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M")
    except ValueError as exc:
        raise AdminValidationError(f"{label} are un format invalid.") from exc


@app.exception_handler(AdminValidationError)
async def admin_validation_error(request: Request, exc: AdminValidationError):
    return return_to_form(request, "error", str(exc))


@app.exception_handler(AdminOperationError)
async def admin_operation_error(request: Request, exc: AdminOperationError):
    return return_to_form(request, "error", str(exc))


@app.exception_handler(IntegrityError)
async def integrity_error(request: Request, exc: IntegrityError):
    return return_to_form(request, "error", "Datele încalcă o regulă de unicitate sau integritate. Verifică valorile introduse.")


@app.exception_handler(RequestValidationError)
async def request_validation_error(request: Request, exc: RequestValidationError):
    return return_to_form(request, "error", "Datele formularului sunt incomplete sau au un format invalid.")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.exception_handler(HTTPException)
async def http_exception(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={"status_code": exc.status_code, "message": exc.detail},
        status_code=exc.status_code,
    )

def get_accessor():
    db = SessionLocal()
    try:
        yield UtilizatoriAccessor(db)
    finally:
        db.close()

def get_carti_accessor():
    db = SessionLocal()
    try:
        yield CartiAccessor(db)
    finally:
        db.close()

def get_categorii_accessor():
    db = SessionLocal()
    try:
        yield CategoriiAccessor(db)
    finally:
        db.close()

def get_setari_accessor():
    db = SessionLocal()
    try:
        yield SetariAccessor(db)
    finally:
        db.close()

def get_alerte_accessor():
    db = SessionLocal()
    try:
        yield AlerteAccessor(db)
    finally:
        db.close()

def get_capitole_accessor():
    db = SessionLocal()
    try:
        yield CapitoleAccessor(db)
    finally:
        db.close()

def get_recenzii_accessor():
    db = SessionLocal()
    try:
        yield RecenziiAccessor(db)
    finally:
        db.close()

def get_comentarii_accessor():
    db = SessionLocal()
    try:
        yield ComentariiAccessor(db)
    finally:
        db.close()

def get_nivele_accessor():
    db = SessionLocal()
    try:
        yield NiveleAccessor(db)
    finally:
        db.close()

def get_evenimente_accessor():
    db = SessionLocal()
    try:
        yield EvenimenteAccessor(db)
    finally:
        db.close()

def get_plati_accessor():
    db = SessionLocal()
    try:
        yield PlatiAccessor(db)
    finally:
        db.close()

def get_cereri_accessor():
    db = SessionLocal()
    try:
        yield CereriRetragereAccessor(db)
    finally:
        db.close()

def get_rapoarte_accessor():
    db = SessionLocal()
    try:
        yield RapoarteAccessor(db)
    finally:
        db.close()

def get_notificari_accessor():
    db = SessionLocal()
    try:
        yield NotificariAccessor(db)
    finally:
        db.close()

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="home.html", 
        context={"request": request}
    )

def get_analitice_accessor():
    db = SessionLocal()
    try:
        yield AnaliticeAccessor(db)
    finally:
        db.close()

@app.get("/utilizatori")
def index(request: Request, accessor: UtilizatoriAccessor = Depends(get_accessor)):
    utilizatori = accessor.get_all_users()
    return templates.TemplateResponse(request=request, name="users_index.html", context={"utilizatori": utilizatori})

@app.get("/utilizatori/detalii/{user_id}")
def details(request: Request, user_id: int, accessor: UtilizatoriAccessor = Depends(get_accessor)):
    utilizator = get_or_404(accessor.get_user_by_id(user_id), "Utilizatorul")
    return templates.TemplateResponse(request=request, name="users_details.html", context={"utilizator": utilizator})

@app.get("/utilizatori/creare")
def create_get(request: Request):
    return templates.TemplateResponse(request=request, name="users_create.html")

@app.post("/utilizatori/creare")
def create_post(
    request: Request,
    nume_utilizator: str = Form(...), 
    email: str = Form(...), 
    parola_hash: str = Form(...),
    rol: str = Form("cititor"), 
    telefon: Optional[str] = Form(None), 
    adresa: Optional[str] = Form(None), 
    data_nasterii: Optional[date] = Form(None),
    accessor: UtilizatoriAccessor = Depends(get_accessor)
):
    accessor.add_entity(require_present(nume_utilizator, "Numele utilizatorului"), require_present(email, "Emailul"), require_present(parola_hash, "Parola demonstrativă"), require_choice(rol, VALID_ROLES, "rol"), telefon, adresa, data_nasterii)
    return redirect_with_feedback("/utilizatori", "success", "Utilizatorul a fost creat.")

@app.get("/utilizatori/editare/{user_id}")
def edit_get(request: Request, user_id: int, accessor: UtilizatoriAccessor = Depends(get_accessor)):
    utilizator = get_or_404(accessor.get_user_by_id(user_id), "Utilizatorul")
    return templates.TemplateResponse(request=request, name="users_edit.html", context={"utilizator": utilizator})

@app.post("/utilizatori/editare/{user_id}")
def edit_post(
    request: Request,
    user_id: int,
    nume_utilizator: str = Form(...), 
    email: str = Form(...), 
    rol: str = Form("cititor"),
    telefon: Optional[str] = Form(None), 
    adresa: Optional[str] = Form(None), 
    data_nasterii: Optional[date] = Form(None),
    accessor: UtilizatoriAccessor = Depends(get_accessor)
):
    get_or_404(accessor.update_entity(user_id, require_present(nume_utilizator, "Numele utilizatorului"), require_present(email, "Emailul"), require_choice(rol, VALID_ROLES, "rol"), telefon, adresa, data_nasterii), "Utilizatorul")
    return redirect_with_feedback("/utilizatori", "success", "Utilizatorul a fost actualizat.")

@app.get("/carti")
def carti_index(request: Request, accessor: CartiAccessor = Depends(get_carti_accessor)):
    carti = accessor.get_all_carti()
    return templates.TemplateResponse(request=request, name="carti_index.html", context={"carti": carti})

@app.get("/carti/creare")
def carti_create_get(request: Request, accessor: CartiAccessor = Depends(get_carti_accessor)):
    # Trimitem lista de autori către View pentru a popula dropdown-ul
    autori = accessor.get_autori_pentru_dropdown()
    return templates.TemplateResponse(request=request, name="carti_create.html", context={"autori": autori})

@app.post("/carti/creare")
def carti_create_post(
    request: Request,
    titlu: str = Form(...), 
    id_autor: int = Form(...), 
    descriere: str = Form(""), 
    stare: str = Form("publicat"),
    accessor: CartiAccessor = Depends(get_carti_accessor)
):
    accessor.add_carte(require_present(titlu, "Titlul"), id_autor, descriere, require_choice(stare, VALID_BOOK_STATES, "stare"))
    return redirect_with_feedback("/carti", "success", "Cartea a fost creată.")

@app.get("/carti/detalii/{carte_id}")
def carti_details(request: Request, carte_id: int, accessor: CartiAccessor = Depends(get_carti_accessor)):
    carte = get_or_404(accessor.get_carte_by_id(carte_id), "Cartea")
    return templates.TemplateResponse(request=request, name="carti_details.html", context={"carte": carte})

@app.get("/carti/editare/{carte_id}")
def carti_edit_get(request: Request, carte_id: int, accessor: CartiAccessor = Depends(get_carti_accessor)):
    carte = get_or_404(accessor.get_carte_by_id(carte_id), "Cartea")
    autori = accessor.get_autori_pentru_dropdown()
    return templates.TemplateResponse(request=request, name="carti_edit.html", context={"carte": carte, "autori": autori})

@app.post("/carti/editare/{carte_id}")
def carti_edit_post(
    request: Request,
    carte_id: int,
    titlu: str = Form(...), 
    id_autor: int = Form(...), 
    descriere: str = Form(""), 
    stare: str = Form("publicat"),
    accessor: CartiAccessor = Depends(get_carti_accessor)
):
    get_or_404(accessor.update_carte(carte_id, require_present(titlu, "Titlul"), id_autor, descriere, require_choice(stare, VALID_BOOK_STATES, "stare")), "Cartea")
    return redirect_with_feedback("/carti", "success", "Cartea a fost actualizată.")

@app.get("/categorii")
def categorii_index(request: Request, accessor: CategoriiAccessor = Depends(get_categorii_accessor)):
    categorii = accessor.get_toate_categoriile()
    return templates.TemplateResponse(request=request, name="categorii_index.html", context={"categorii": categorii})

@app.get("/categorii/creare")
def categorii_create_get(request: Request):
    return templates.TemplateResponse(request=request, name="categorii_create.html", context={"request": request})

@app.post("/categorii/creare")
def categorii_create_post(
    request: Request,
    nume: str = Form(...),
    descriere: Optional[str] = Form(None),
    accessor: CategoriiAccessor = Depends(get_categorii_accessor)
):
    accessor.add_categorie(require_present(nume, "Numele categoriei"), descriere)
    return redirect_with_feedback("/categorii", "success", "Categoria a fost creată.")

@app.get("/categorii/editare/{cat_id}")
def categorii_edit_get(request: Request, cat_id: int, accessor: CategoriiAccessor = Depends(get_categorii_accessor)):
    categorie = get_or_404(accessor.get_categorie_by_id(cat_id), "Categoria")
    return templates.TemplateResponse(request=request, name="categorii_edit.html", context={"categorie": categorie})

@app.post("/categorii/editare/{cat_id}")
def categorii_edit_post(
    request: Request,
    cat_id: int,
    nume: str = Form(...),
    descriere: Optional[str] = Form(None),
    accessor: CategoriiAccessor = Depends(get_categorii_accessor)
):
    get_or_404(accessor.update_categorie(cat_id, require_present(nume, "Numele categoriei"), descriere), "Categoria")
    return redirect_with_feedback("/categorii", "success", "Categoria a fost actualizată.")

@app.get("/setari")
def setari_index(request: Request, accessor: SetariAccessor = Depends(get_setari_accessor)):
    setari = accessor.get_toate_setarile()
    return templates.TemplateResponse(request=request, name="setari_index.html", context={"setari": setari})

@app.get("/setari/creare")
def setari_create_get(request: Request):
    return templates.TemplateResponse(request=request, name="setari_create.html", context={"request": request})

@app.post("/setari/creare")
def setari_create_post(
    request: Request,
    nume_setare: str = Form(...),
    valoare_setare: str = Form(...),
    accessor: SetariAccessor = Depends(get_setari_accessor)
):
    accessor.add_setare(require_present(nume_setare, "Numele setării"), require_present(valoare_setare, "Valoarea setării"))
    return redirect_with_feedback("/setari", "success", "Setarea a fost creată.")

@app.get("/setari/editare/{setare_id}")
def setari_edit_get(request: Request, setare_id: int, accessor: SetariAccessor = Depends(get_setari_accessor)):
    setare = get_or_404(accessor.get_setare_by_id(setare_id), "Setarea")
    return templates.TemplateResponse(request=request, name="setari_edit.html", context={"setare": setare})

@app.post("/setari/editare/{setare_id}")
def setari_edit_post(
    request: Request,
    setare_id: int,
    nume_setare: str = Form(...),
    valoare_setare: str = Form(...),
    accessor: SetariAccessor = Depends(get_setari_accessor)
):
    get_or_404(accessor.update_setare(setare_id, require_present(nume_setare, "Numele setării"), require_present(valoare_setare, "Valoarea setării")), "Setarea")
    return redirect_with_feedback("/setari", "success", "Setarea a fost actualizată.")

@app.get("/alerte")
def alerte_index(request: Request, accessor: AlerteAccessor = Depends(get_alerte_accessor)):
    alerte = accessor.get_toate_alertele()
    return templates.TemplateResponse(request=request, name="alerte_index.html", context={"alerte": alerte})

@app.get("/alerte/creare")
def alerte_create_get(request: Request):
    return templates.TemplateResponse(request=request, name="alerte_create.html", context={"request": request})

@app.post("/alerte/creare")
def alerte_create_post(
    request: Request,
    mesaj: str = Form(...),
    tip_alerta: str = Form("info"),
    accessor: AlerteAccessor = Depends(get_alerte_accessor)
):
    accessor.add_alerta(require_present(mesaj, "Mesajul"), require_choice(tip_alerta, VALID_ALERT_TYPES, "tipul alertei"))
    return redirect_with_feedback("/alerte", "success", "Alerta a fost creată.")

@app.get("/alerte/editare/{alerta_id}")
def alerte_edit_get(request: Request, alerta_id: int, accessor: AlerteAccessor = Depends(get_alerte_accessor)):
    alerta = get_or_404(accessor.get_alerta_by_id(alerta_id), "Alerta")
    return templates.TemplateResponse(request=request, name="alerte_edit.html", context={"alerta": alerta})

@app.post("/alerte/editare/{alerta_id}")
def alerte_edit_post(
    request: Request,
    alerta_id: int,
    mesaj: str = Form(...),
    tip_alerta: str = Form("info"),
    accessor: AlerteAccessor = Depends(get_alerte_accessor)
):
    get_or_404(accessor.update_alerta(alerta_id, require_present(mesaj, "Mesajul"), require_choice(tip_alerta, VALID_ALERT_TYPES, "tipul alertei")), "Alerta")
    return redirect_with_feedback("/alerte", "success", "Alerta a fost actualizată.")

@app.get("/capitole")
def capitole_index(request: Request, accessor: CapitoleAccessor = Depends(get_capitole_accessor)):
    capitole = accessor.get_toate_capitolele()
    return templates.TemplateResponse(request=request, name="capitole_index.html", context={"capitole": capitole})

@app.get("/capitole/detalii/{cap_id}")
def capitole_details(request: Request, cap_id: int, accessor: CapitoleAccessor = Depends(get_capitole_accessor)):
    capitol = get_or_404(accessor.get_capitol_by_id(cap_id), "Capitolul")
    return templates.TemplateResponse(request=request, name="capitole_details.html", context={"capitol": capitol})

@app.get("/capitole/creare")
def capitole_create_get(request: Request, accessor: CapitoleAccessor = Depends(get_capitole_accessor)):
    carti = accessor.get_carti_pentru_dropdown()
    return templates.TemplateResponse(request=request, name="capitole_create.html", context={"carti": carti})

@app.post("/capitole/creare")
def capitole_create_post(
    request: Request,
    id_carte: int = Form(...),
    numar_capitol: int = Form(...),
    titlu: str = Form(...),
    continut: str = Form(...),
    cost_puncte: int = Form(0),
    stare: str = Form("ciorna"),
    este_gratuit: Optional[str] = Form(None), # Checkbox-ul vine ca 'on' sau None
    accessor: CapitoleAccessor = Depends(get_capitole_accessor)
):
    is_free = True if este_gratuit == 'on' else False
    if numar_capitol < 1:
        raise AdminValidationError("Numărul capitolului trebuie să fie cel puțin 1.")
    require_non_negative(cost_puncte, "Costul în puncte")
    require_choice(stare, VALID_BOOK_STATES, "stare")
    if not is_free and cost_puncte == 0:
        raise AdminValidationError("Un capitol plătit trebuie să aibă un cost mai mare decât zero.")
    accessor.add_capitol(id_carte, numar_capitol, require_present(titlu, "Titlul"), require_present(continut, "Conținutul"), is_free, cost_puncte, stare)
    return redirect_with_feedback("/capitole", "success", "Capitolul a fost creat.")

@app.get("/capitole/editare/{cap_id}")
def capitole_edit_get(request: Request, cap_id: int, accessor: CapitoleAccessor = Depends(get_capitole_accessor)):
    capitol = get_or_404(accessor.get_capitol_by_id(cap_id), "Capitolul")
    carti = accessor.get_carti_pentru_dropdown()
    return templates.TemplateResponse(request=request, name="capitole_edit.html", context={"capitol": capitol, "carti": carti})

@app.post("/capitole/editare/{cap_id}")
def capitole_edit_post(
    request: Request,
    cap_id: int,
    id_carte: int = Form(...),
    numar_capitol: int = Form(...),
    titlu: str = Form(...),
    continut: str = Form(...),
    cost_puncte: int = Form(0),
    stare: str = Form("ciorna"),
    este_gratuit: Optional[str] = Form(None),
    accessor: CapitoleAccessor = Depends(get_capitole_accessor)
):
    is_free = True if este_gratuit == 'on' else False
    if numar_capitol < 1:
        raise AdminValidationError("Numărul capitolului trebuie să fie cel puțin 1.")
    require_non_negative(cost_puncte, "Costul în puncte")
    require_choice(stare, VALID_BOOK_STATES, "stare")
    if not is_free and cost_puncte == 0:
        raise AdminValidationError("Un capitol plătit trebuie să aibă un cost mai mare decât zero.")
    get_or_404(accessor.update_capitol(cap_id, id_carte, numar_capitol, require_present(titlu, "Titlul"), require_present(continut, "Conținutul"), is_free, cost_puncte, stare), "Capitolul")
    return redirect_with_feedback("/capitole", "success", "Capitolul a fost actualizat.")

@app.get("/recenzii")
def recenzii_index(request: Request, accessor: RecenziiAccessor = Depends(get_recenzii_accessor)):
    recenzii = accessor.get_toate_recenziile()
    return templates.TemplateResponse(request=request, name="recenzii_index.html", context={"recenzii": recenzii})

@app.get("/recenzii/editare/{rec_id}")
def recenzii_edit_get(request: Request, rec_id: int, accessor: RecenziiAccessor = Depends(get_recenzii_accessor)):
    recenzie = get_or_404(accessor.get_recenzie_by_id(rec_id), "Recenzia")
    return templates.TemplateResponse(request=request, name="recenzii_edit.html", context={"recenzie": recenzie})

@app.post("/recenzii/editare/{rec_id}")
def recenzii_edit_post(
    request: Request,
    rec_id: int,
    nota: int = Form(...),
    text_comentariu: str = Form(...),
    accessor: RecenziiAccessor = Depends(get_recenzii_accessor)
):
    if not 1 <= nota <= 5:
        raise AdminValidationError("Nota trebuie să fie între 1 și 5.")
    get_or_404(accessor.update_recenzie(rec_id, nota, require_present(text_comentariu, "Textul recenziei")), "Recenzia")
    return redirect_with_feedback("/recenzii", "success", "Recenzia a fost actualizată.")

@app.get("/comentarii")
def comentarii_index(request: Request, accessor: ComentariiAccessor = Depends(get_comentarii_accessor)):
    comentarii = accessor.get_toate_comentariile()
    return templates.TemplateResponse(request=request, name="comentarii_index.html", context={"comentarii": comentarii})

@app.get("/comentarii/editare/{com_id}")
def comentarii_edit_get(request: Request, com_id: int, accessor: ComentariiAccessor = Depends(get_comentarii_accessor)):
    comentariu = get_or_404(accessor.get_comentariu_by_id(com_id), "Comentariul")
    return templates.TemplateResponse(request=request, name="comentarii_edit.html", context={"comentariu": comentariu})

@app.post("/comentarii/editare/{com_id}")
def comentarii_edit_post(
    request: Request,
    com_id: int,
    continut: str = Form(...),
    accessor: ComentariiAccessor = Depends(get_comentarii_accessor)
):
    get_or_404(accessor.update_comentariu(com_id, require_present(continut, "Conținutul comentariului")), "Comentariul")
    return redirect_with_feedback("/comentarii", "success", "Comentariul a fost actualizat.")

@app.get("/abonamente")
def abonamente_index(request: Request, accessor: NiveleAccessor = Depends(get_nivele_accessor)):
    nivele = accessor.get_toate_nivelele()
    return templates.TemplateResponse(request=request, name="abonamente_index.html", context={"nivele": nivele})

@app.get("/abonamente/creare")
def abonamente_create_get(request: Request):
    return templates.TemplateResponse(request=request, name="abonamente_create.html", context={"request": request})

@app.post("/abonamente/creare")
def abonamente_create_post(
    request: Request,
    nume: str = Form(...),
    pret_real: float = Form(...),
    descriere_beneficii: Optional[str] = Form(None),
    accessor: NiveleAccessor = Depends(get_nivele_accessor)
):
    require_non_negative(pret_real, "Prețul")
    accessor.add_nivel(require_present(nume, "Numele abonamentului"), pret_real, descriere_beneficii)
    return redirect_with_feedback("/abonamente", "success", "Nivelul de abonament a fost creat.")

@app.get("/abonamente/editare/{nivel_id}")
def abonamente_edit_get(request: Request, nivel_id: int, accessor: NiveleAccessor = Depends(get_nivele_accessor)):
    nivel = get_or_404(accessor.get_nivel_by_id(nivel_id), "Nivelul de abonament")
    return templates.TemplateResponse(request=request, name="abonamente_edit.html", context={"nivel": nivel})

@app.post("/abonamente/editare/{nivel_id}")
def abonamente_edit_post(
    request: Request,
    nivel_id: int,
    nume: str = Form(...),
    pret_real: float = Form(...),
    descriere_beneficii: Optional[str] = Form(None),
    accessor: NiveleAccessor = Depends(get_nivele_accessor)
):
    require_non_negative(pret_real, "Prețul")
    get_or_404(accessor.update_nivel(nivel_id, require_present(nume, "Numele abonamentului"), pret_real, descriere_beneficii), "Nivelul de abonament")
    return redirect_with_feedback("/abonamente", "success", "Nivelul de abonament a fost actualizat.")

@app.get("/evenimente")
def evenimente_index(request: Request, accessor: EvenimenteAccessor = Depends(get_evenimente_accessor)):
    evenimente = accessor.get_toate_evenimentele()
    return templates.TemplateResponse(request=request, name="evenimente_index.html", context={"evenimente": evenimente})

@app.get("/evenimente/creare")
def evenimente_create_get(request: Request):
    return templates.TemplateResponse(request=request, name="evenimente_create.html", context={"request": request})

@app.post("/evenimente/creare")
def evenimente_create_post(
    request: Request,
    nume: str = Form(...),
    recompensa_puncte: int = Form(...),
    data_inceput: str = Form(...),
    data_sfarsit: str = Form(...),
    este_activ: Optional[str] = Form(None),
    accessor: EvenimenteAccessor = Depends(get_evenimente_accessor)
):
    is_active = True if este_activ == 'on' else False
    # Parsăm string-urile venite din input type="datetime-local"
    dt_inceput = parse_form_datetime(data_inceput, "Data de început")
    dt_sfarsit = parse_form_datetime(data_sfarsit, "Data de sfârșit")
    require_non_negative(recompensa_puncte, "Recompensa în puncte")
    if dt_sfarsit <= dt_inceput:
        raise AdminValidationError("Data de sfârșit trebuie să fie după data de început.")
    accessor.add_eveniment(require_present(nume, "Numele evenimentului"), recompensa_puncte, dt_inceput, dt_sfarsit, is_active)
    return redirect_with_feedback("/evenimente", "success", "Evenimentul a fost creat.")

@app.get("/evenimente/editare/{ev_id}")
def evenimente_edit_get(request: Request, ev_id: int, accessor: EvenimenteAccessor = Depends(get_evenimente_accessor)):
    eveniment = get_or_404(accessor.get_eveniment_by_id(ev_id), "Evenimentul")
    return templates.TemplateResponse(request=request, name="evenimente_edit.html", context={"eveniment": eveniment})

@app.post("/evenimente/editare/{ev_id}")
def evenimente_edit_post(
    request: Request,
    ev_id: int,
    nume: str = Form(...),
    recompensa_puncte: int = Form(...),
    data_inceput: str = Form(...),
    data_sfarsit: str = Form(...),
    este_activ: Optional[str] = Form(None),
    accessor: EvenimenteAccessor = Depends(get_evenimente_accessor)
):
    is_active = True if este_activ == 'on' else False
    dt_inceput = parse_form_datetime(data_inceput, "Data de început")
    dt_sfarsit = parse_form_datetime(data_sfarsit, "Data de sfârșit")
    require_non_negative(recompensa_puncte, "Recompensa în puncte")
    if dt_sfarsit <= dt_inceput:
        raise AdminValidationError("Data de sfârșit trebuie să fie după data de început.")
    get_or_404(accessor.update_eveniment(ev_id, require_present(nume, "Numele evenimentului"), recompensa_puncte, dt_inceput, dt_sfarsit, is_active), "Evenimentul")
    return redirect_with_feedback("/evenimente", "success", "Evenimentul a fost actualizat.")

@app.get("/plati")
def plati_index(request: Request, accessor: PlatiAccessor = Depends(get_plati_accessor)):
    plati = accessor.get_toate_platile()
    return templates.TemplateResponse(request=request, name="plati_index.html", context={"plati": plati})

@app.get("/plati/rambursare/{plata_id}")
def plati_rambursare_get(request: Request, plata_id: int, accessor: PlatiAccessor = Depends(get_plati_accessor)):
    plata = get_or_404(accessor.get_plata_by_id(plata_id), "Plata")
    if plata.stare != "finalizat":
        raise AdminValidationError("Doar o plată finalizată poate fi rambursată.")
    return templates.TemplateResponse(request=request, name="plati_rambursare.html", context={"plata": plata, "admini": accessor.get_admini()})


@app.post("/plati/rambursare/{plata_id}")
def plati_rambursare_post(
    request: Request,
    plata_id: int,
    id_admin_rambursare: int = Form(...),
    motiv_rambursare: str = Form(...),
    accessor: PlatiAccessor = Depends(get_plati_accessor),
):
    get_or_404(accessor.anuleaza_plata_si_servicii(plata_id, id_admin_rambursare, require_present(motiv_rambursare, "Motivul rambursării")), "Plata")
    return redirect_with_feedback("/plati", "success", "Rambursarea simulată a fost înregistrată.")

@app.get("/cereri-retragere")
def cereri_index(request: Request, accessor: CereriRetragereAccessor = Depends(get_cereri_accessor)):
    cereri = accessor.get_toate_cererile()
    return templates.TemplateResponse(request=request, name="cereri_index.html", context={"cereri": cereri})

@app.get("/cereri-retragere/procesare/{cerere_id}")
def cereri_procesare_get(request: Request, cerere_id: int, accessor: CereriRetragereAccessor = Depends(get_cereri_accessor)):
    cerere = get_or_404(accessor.get_cerere_by_id(cerere_id), "Cererea de retragere")
    if cerere.stare != "in_asteptare":
        raise AdminValidationError("Această cerere a fost deja procesată.")
    return templates.TemplateResponse(request=request, name="cereri_procesare.html", context={"cerere": cerere, "admini": accessor.get_admini()})

@app.post("/cereri-retragere/procesare/{cerere_id}")
def cereri_procesare_post(
    request: Request,
    cerere_id: int,
    stare: str = Form(...),
    id_admin_procesare: int = Form(...),
    observatii: Optional[str] = Form(None),
    accessor: CereriRetragereAccessor = Depends(get_cereri_accessor)
):
    require_choice(stare, VALID_WITHDRAWAL_STATES, "decizia")
    get_or_404(accessor.proceseaza_cerere(cerere_id, stare, id_admin_procesare, observatii), "Cererea de retragere")
    return redirect_with_feedback("/cereri-retragere", "success", "Cererea a fost procesată și înregistrată în audit.")

@app.get("/rapoarte")
def rapoarte_index(request: Request, accessor: RapoarteAccessor = Depends(get_rapoarte_accessor)):
    rapoarte = accessor.get_toate_rapoartele()
    return templates.TemplateResponse(request=request, name="rapoarte_index.html", context={"rapoarte": rapoarte})

@app.get("/rapoarte/rezolvare/{rap_id}")
def rapoarte_rezolvare_get(request: Request, rap_id: int, accessor: RapoarteAccessor = Depends(get_rapoarte_accessor)):
    raport = get_or_404(accessor.get_raport_by_id(rap_id), "Raportul")
    admini = accessor.get_admini()
    return templates.TemplateResponse(request=request, name="rapoarte_rezolvare.html", context={"raport": raport, "admini": admini})

@app.post("/rapoarte/rezolvare/{rap_id}")
def rapoarte_rezolvare_post(
    request: Request,
    rap_id: int,
    stare: str = Form(...),
    id_admin_rezolvare: int = Form(...),
    accessor: RapoarteAccessor = Depends(get_rapoarte_accessor)
):
    require_choice(stare, VALID_REPORT_STATES, "decizia")
    get_or_404(accessor.rezolva_raport(rap_id, stare, id_admin_rezolvare), "Raportul")
    return redirect_with_feedback("/rapoarte", "success", "Raportul a fost soluționat.")

@app.get("/notificari")
def notificari_index(request: Request, accessor: NotificariAccessor = Depends(get_notificari_accessor)):
    notificari = accessor.get_toate_notificarile()
    return templates.TemplateResponse(request=request, name="notificari_index.html", context={"notificari": notificari})

@app.get("/notificari/creare")
def notificari_creare_get(request: Request, accessor: NotificariAccessor = Depends(get_notificari_accessor)):
    utilizatori = accessor.get_utilizatori()
    return templates.TemplateResponse(request=request, name="notificari_create.html", context={"utilizatori": utilizatori})

@app.post("/notificari/creare")
def notificari_creare_post(
    request: Request,
    id_utilizator: int = Form(...),
    titlu: str = Form(...),
    mesaj: str = Form(...),
    accessor: NotificariAccessor = Depends(get_notificari_accessor)
):
    accessor.add_notificare(id_utilizator, require_present(titlu, "Titlul"), require_present(mesaj, "Mesajul"))
    return redirect_with_feedback("/notificari", "success", "Notificarea a fost trimisă.")

@app.get("/analitice/abonamente")
def analitice_abonamente(request: Request, accessor: AnaliticeAccessor = Depends(get_analitice_accessor)):
    abonamente = accessor.get_istoric_abonamente()
    return templates.TemplateResponse(request=request, name="analitice_abonamente.html", context={"abonamente": abonamente})

@app.get("/analitice/puncte")
def analitice_puncte(request: Request, accessor: AnaliticeAccessor = Depends(get_analitice_accessor)):
    tranzactii = accessor.get_tranzactii_puncte()
    return templates.TemplateResponse(request=request, name="analitice_puncte.html", context={"tranzactii": tranzactii})
