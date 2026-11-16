# Creator Hub

Creator Hub este un MVP database-first pentru o platformă de tip creator. Aplicația separă catalogul public de administrare, dar folosește aceeași bază de date PostgreSQL, aceeași aplicație FastAPI și aceeași origine HTTP.

## Componente

- Platformă publică React: catalogul cărților publicate și citirea capitolelor gratuite.
- Sesiuni guest: un vizitator primește un cookie opac; nu se creează un rând fals în `utilizatori`.
- Admin MVC: operații de administrare pentru conținut, comunitate, finanțe și sistem.
- API REST: endpointuri Pydantic pentru categorii și catalogul public.
- Documentație OpenAPI: disponibilă numai unui administrator autentificat.

## Structură

```text
PPAW/
├── alembic/                    # Migrări PostgreSQL
├── backend/
│   ├── admin/                  # Module MVC: content, community, finance, operations, docs
│   ├── api_router.py           # API-ul categoriilor
│   ├── public_catalog_router.py # API-ul catalogului public
│   ├── access_sessions.py      # Cookie-uri și sesiuni persistate
│   ├── authentication.py       # Derivarea parolei și verificarea adminului
│   ├── config.py               # Configurare comună
│   ├── crud.py                 # Accesori SQLAlchemy
│   ├── models.py               # Modele ORM
│   └── main.py                 # Punct de intrare FastAPI
├── frontend/                   # React/Vite; `dist/` este produs de build
├── alembic.ini
├── requirements.txt
└── README.md
```

`backend/main.py` păstrează doar configurarea aplicației, securitatea zonei admin, excepțiile și servirea frontendului. Rutele MVC sunt împărțite pe domenii în `backend/admin/`.

## Instalare locală

### 1. Mediu Python și dependențe

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Baza de date și migrările

Configurează PostgreSQL prin variabila `DATABASE_URL` sau actualizează configurația locală folosită de aplicație. Apoi rulează migrările:

```powershell
.\.venv\Scripts\alembic.exe upgrade head
```

### 3. Frontendul de producție

FastAPI servește fișierele compilate din `frontend/dist`; Vite nu este necesar la demonstrația finală.

```powershell
Set-Location frontend
npm ci
npm run build
Set-Location ..
```

Pentru dezvoltarea React se poate folosi și `npm run dev`. Configurația Vite trimite automat cererile `/api` către `http://127.0.0.1:8080`.

### 4. Primul administrator

Niciun cont cu parolă implicită nu este introdus în cod sau în migrări. Creează explicit un administrator; parola este solicitată interactiv și stocată derivată cu `scrypt`:

```powershell
.\.venv\Scripts\python.exe -m backend.create_admin admin admin@example.test
```

### 5. Pornirea aplicației

Din rădăcina proiectului:

```powershell
.\.venv\Scripts\uvicorn.exe backend.main:app --reload --port 8080
```

Alternativ, din directorul `backend`:

```powershell
..\.venv\Scripts\uvicorn.exe main:app --reload --port 8080
```

Ambele comenzi sunt suportate.

## Adrese locale

| Adresă | Acces |
| --- | --- |
| [Platformă publică](http://127.0.0.1:8080/) | Public; catalog și capitole gratuite |
| [Login admin](http://127.0.0.1:8080/admin/login) | Cont cu rol `admin` |
| [MVC admin](http://127.0.0.1:8080/admin) | Sesiune admin |
| [CRUD categorii](http://127.0.0.1:8080/admin/categorii-api) | Sesiune admin; consumă `GET`, `POST`, `PUT`, `DELETE` din `/api/categorii` |
| [Swagger/OpenAPI](http://127.0.0.1:8080/admin/docs) | Sesiune admin; folosește același cookie ca MVC-ul |

`/docs`, `/redoc` și `/openapi.json` redirecționează spre zona administrativă. După autentificare, documentația și MVC-ul utilizează același cookie `ppaw_access`.

## API-uri

- `/api/v1/carti` și `/api/v1/carti/{id}` sunt publice și oferă catalogul publicat.
- `/api/v1/capitole/{id}/citire` permite numai capitole gratuite și creează/actualizează sesiunea guest.
- `GET /api/categorii` este disponibil pentru citire.
- `POST`, `PUT` și `DELETE /api/categorii` cer o sesiune de administrator.

## Git și fișiere locale

`.gitignore` exclude artefactele locale: medii virtuale, `__pycache__`, fișiere `.pyc`, directoare `tmp/`, buildul React, `.env`, loguri și cache-uri de test. Nu adăuga manual `frontend/dist`, fișiere temporare sau cache-uri Python în commituri.

Pentru istoricul proiectului, păstrează commiturile mici și tematice, cu cel mult cinci fișiere per commit. Push-ul și PR-ul se fac după verificarea locală a tuturor commiturilor.
