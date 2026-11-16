# Creator Hub — Platformă Integrată de Tip Creator (MVC & RESTful API)

Aplicație web robustă dezvoltată cu **FastAPI**, **SQLAlchemy ORM** și **Jinja2 (MVC)**, completată cu un modul dedicat de **RESTful API** pentru consumatori externi. Proiectul este, în prezent, un Minimum Viable Product (MVP) pentru administrarea completă a unei platforme de tip creator (gestiune utilizatori, conținut editorial, monetizare, abonamente, moderare și analitice).

---

## Arhitectura Aplicației

Proiectul folosește o arhitectură modulară și curată:
1. **Nivelul de Acces la Date (ORM):** Modele mapate cu SQLAlchemy și gestionarea migrărilor prin **Alembic**.
2. **Nivelul de Business / Servicii (CRUD & Logică):** Accesori and-logic separați pentru fiecare entitate în parte, gestionând constrângerile și operațiile în cascadă.
3. **Interfața Administrativă (MVC):** Panou de control bazat pe șabloane Jinja2 și Bootstrap 5 pentru administrare vizuală completă.
4. **Nivelul API RESTful:** Rute dedicate pentru clienții externi, structurate prin `APIRouter`, folosind scheme Pydantic pentru validare și mapare automată.

---

## Entități Administrate (Modulul Admin & API)

* **Utilizatori:** Gestiune conturi, roluri (`cititor`, `autor`, `admin`), stare cont și puncte.
* **Cărți & Capitole:** Publicare de conținut, stabilire capitole gratuite sau cu plată (puncte).
* **Economie și Finanțe:** Nivele de abonament (Tiers), evenimente promoționale, istoric plăți și cereri de retragere pentru autori.
* **Moderare și Suport:** Recenzii, comentarii, rapoarte de conținut și notificări de sistem.
* **Analitice (Read-Only):** Registru tranzacții puncte, istoric subscripții și vizualizări.

---

## Pași de Instalare și Rulare locală

### 1. Clonarea repository-ului și configurarea mediului

Creează și activează un mediu virtual Python în directorul rădăcină:
```bash
python -m venv .venv
# Pe Windows:
.venv\Scripts\activate
# Pe Mac/Linux:
source .venv/bin/activate
```

### 2. Instalarea dependențelor

Instalează pachetele necesare specificate în fișierul de configurare:

```bash
pip install -r requirements.txt
```

### 3. Configurarea bazei de date

Asigură-te că ai configurat conexiunea la baza de date (PostgreSQL) în mediul tău local. Aplică migrările Alembic pentru a genera structura completă a tabelelor:

```bash
alembic upgrade head
```

### 4. Compilarea frontendului pentru producție

Catalogul React nu este servit de Vite în timpul demonstrației. Instalează
dependințele o singură dată și generează artefactele statice:

```bash
cd frontend
npm ci
npm run build
cd ..
```

### 5. Crearea primului administrator

Contul de administrator nu este introdus cu o parolă fixă în cod sau în
migrări. Creează-l local după aplicarea migrărilor; comanda cere parola
interactiv și o stochează derivată cu `scrypt` în baza de date:

```bash
.venv\Scripts\python.exe -m backend.create_admin admin admin@example.test
```

### 6. Pornirea aplicației

Rulează serverul folosind uvicorn (aplicația rulează pe portul 8080):

```bash
uvicorn backend.main:app --reload --port 8080
```

## Ghid de utilizare și testare

* **Platforma publică**: [http://127.0.0.1:8080/](http://127.0.0.1:8080/) afișează catalogul React și permite citirea capitolelor gratuite. Vizitatorii guest primesc o sesiune opacă, fără rând nou în `utilizatori`.

* **Panoul administrativ (MVC)**: [http://127.0.0.1:8080/admin/login](http://127.0.0.1:8080/admin/login) cere un cont cu rolul `admin`; după autentificare, panoul este la [http://127.0.0.1:8080/admin](http://127.0.0.1:8080/admin).

* **Frontend CRUD pentru laborator**: [http://127.0.0.1:8080/admin/categorii-api](http://127.0.0.1:8080/admin/categorii-api) consumă operațiile `GET`, `POST`, `PUT` și `DELETE` de la `/api/categorii`. Operațiile care modifică datele cer sesiunea administratorului.

* **Documentația API (Swagger)**: [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs) documentează API-ul. Nu este nevoie de DNS pentru rularea locală; pentru publicare, un reverse proxy poate direcționa domeniul către același proces FastAPI, fără a expune porturi diferite pentru frontend și API.

## Structura Proiectului

```
PPAW/
│
├── alembic/              # Migrări bază de date (Alembic)
├── backend/              # Logica aplicației FastAPI
│   ├── api_router.py     # Rutele dedicate pentru REST API (Lab 7)
│   ├── crud.py           # Accesori și logică de business / baza de date
│   ├── main.py           # Punctul de intrare în aplicație și rutele MVC
│   └── models.py         # Modelele SQLAlchemy
├── frontend/             # Catalog React și interfața CRUD pentru API
├── backend/templates/    # Fișierele HTML (Jinja2) pentru panoul de admin
├── alembic.ini           # Configurare Alembic
├── requirements.txt      # Dependențe Python
└── README.md             # Documentația proiectului
```
---
