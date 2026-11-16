"""Creează interactiv primul cont de administrator în baza de date locală.

Rulare din rădăcina proiectului:
    .venv\\Scripts\\python.exe -m backend.create_admin nume email@example.com
"""

from __future__ import annotations

import argparse
import getpass

try:
    from .authentication import hash_password
    from .crud import SessionLocal
    from .models import Utilizatori
except ImportError:
    from authentication import hash_password
    from crud import SessionLocal
    from models import Utilizatori


def main() -> None:
    parser = argparse.ArgumentParser(description='Creeaza un administrator Creator Hub.')
    parser.add_argument('nume_utilizator')
    parser.add_argument('email')
    arguments = parser.parse_args()

    password = getpass.getpass('Parola administrator (minim 10 caractere): ')
    confirmation = getpass.getpass('Repeta parola: ')
    if password != confirmation:
        parser.error('Parolele nu coincid.')
    if len(password) < 10:
        parser.error('Parola trebuie sa aiba cel putin 10 caractere.')

    db = SessionLocal()
    try:
        existing = db.query(Utilizatori).filter(
            (Utilizatori.nume_utilizator == arguments.nume_utilizator)
            | (Utilizatori.email == arguments.email)
        ).first()
        if existing:
            parser.error('Numele de utilizator sau emailul exista deja.')
        db.add(Utilizatori(
            nume_utilizator=arguments.nume_utilizator,
            email=arguments.email,
            parola_hash=hash_password(password),
            rol='admin',
            stare_cont='activ',
            puncte=0,
        ))
        db.commit()
    finally:
        db.close()
    print('Administratorul a fost creat. Il poti folosi la /admin/login.')


if __name__ == '__main__':
    main()
