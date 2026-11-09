# Creator Hub — panou administrativ demonstrativ

Aplicație FastAPI/Jinja pentru administrarea unei platforme de tip creator: utilizatori, conținut, abonamente, plăți simulate, puncte și moderare.

## Pornire locală

1. Creează și activează un mediu virtual Python.
2. Instalează dependențele: `pip install -r requirements.txt`.
3. Configurează `DATABASE_URL` în mediul local înainte de rulare; nu păstra credențiale reale în sursă.
4. Aplică migrările: `alembic upgrade head`.
5. Pornește panoul din rădăcina proiectului: `uvicorn backend.main:app --reload`.

Panoul este disponibil implicit la `http://127.0.0.1:8000`.

## Frontend Vite

Directorul `frontend/` este un prototip React separat și nu este încă conectat la panoul Jinja sau la rute JSON. Pentru demo-ul actual, interfața administrativă este cea servită de FastAPI.
