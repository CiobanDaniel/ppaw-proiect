"""Autentificare locală pentru panoul administrativ.

Parolele sunt derivate cu ``hashlib.scrypt`` din biblioteca standard; nu sunt
stocate și nu sunt comparate în clar.
"""

from __future__ import annotations

import base64
from datetime import date
import hashlib
import hmac
import os

from sqlalchemy import or_
from sqlalchemy.orm import Session

try:
    from .models import Utilizatori
except ImportError:
    from models import Utilizatori


_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1
_SALT_SIZE = 16


def hash_password(password: str) -> str:
    if len(password) < 10:
        raise ValueError('Parola trebuie să aibă cel puțin 10 caractere.')
    salt = os.urandom(_SALT_SIZE)
    derived_key = hashlib.scrypt(password.encode('utf-8'), salt=salt, n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P)
    return 'scrypt${}${}${}${}${}'.format(
        _SCRYPT_N,
        _SCRYPT_R,
        _SCRYPT_P,
        base64.b64encode(salt).decode('ascii'),
        base64.b64encode(derived_key).decode('ascii'),
    )


def verify_password(password: str, encoded_password: str) -> bool:
    try:
        algorithm, n, r, p, salt, expected = encoded_password.split('$')
        if algorithm != 'scrypt':
            return False
        derived_key = hashlib.scrypt(
            password.encode('utf-8'),
            salt=base64.b64decode(salt),
            n=int(n),
            r=int(r),
            p=int(p),
        )
        return hmac.compare_digest(derived_key, base64.b64decode(expected))
    except (ValueError, TypeError, base64.binascii.Error):
        return False


def authenticate_admin(db: Session, identifier: str, password: str) -> Utilizatori | None:
    identifier = identifier.strip()
    admin = db.query(Utilizatori).filter(
        Utilizatori.rol == 'admin',
        or_(Utilizatori.nume_utilizator == identifier, Utilizatori.email == identifier),
    ).first()
    if not admin or not verify_password(password, admin.parola_hash):
        return None
    admin.data_ultimei_logari = date.today()
    db.commit()
    db.refresh(admin)
    return admin
