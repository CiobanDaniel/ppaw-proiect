"""Servicii pentru sesiuni de acces guest sau autentificate."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import hashlib
import secrets

from sqlalchemy.orm import Session
from fastapi import Response

try:
    from .models import SesiuniAcces
except ImportError:
    from models import SesiuniAcces


GUEST_SESSION_DAYS = 30
ACCESS_COOKIE_NAME = 'ppaw_access'


@dataclass(frozen=True)
class AccessSessionResult:
    session: SesiuniAcces
    token_to_set: str | None


class AccessSessionService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def _is_active(session: SesiuniAcces, now: datetime) -> bool:
        return not session.revocata_la and (session.expira_la is None or session.expira_la > now)

    def get_or_create_guest_session(self, raw_token: str | None) -> AccessSessionResult:
        now = datetime.now(UTC)
        if raw_token:
            session = self.db.query(SesiuniAcces).filter(
                SesiuniAcces.token_hash == self._hash_token(raw_token)
            ).first()
            if session and self._is_active(session, now):
                session.data_ultima_activitate = now
                self.db.commit()
                self.db.refresh(session)
                return AccessSessionResult(session=session, token_to_set=None)

        token = secrets.token_urlsafe(32)
        session = SesiuniAcces(
            token_hash=self._hash_token(token),
            data_ultima_activitate=now,
            expira_la=now + timedelta(days=GUEST_SESSION_DAYS),
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return AccessSessionResult(session=session, token_to_set=token)

    def get_active_session(self, raw_token: str | None) -> SesiuniAcces | None:
        """Returnează sesiunea validă fără a crea una nouă."""
        if not raw_token:
            return None
        session = self.db.query(SesiuniAcces).filter(
            SesiuniAcces.token_hash == self._hash_token(raw_token)
        ).first()
        if not session or not self._is_active(session, datetime.now(UTC)):
            return None
        session.data_ultima_activitate = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(session)
        return session

    def associate_user(self, session: SesiuniAcces, user_id: int) -> SesiuniAcces:
        """Transformă o sesiune guest existentă într-o sesiune autentificată."""
        session.id_utilizator = user_id
        session.data_ultima_activitate = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(session)
        return session

    def revoke_session(self, raw_token: str | None) -> None:
        session = self.get_active_session(raw_token)
        if session:
            session.revocata_la = datetime.now(UTC)
            self.db.commit()


def set_access_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=token,
        max_age=GUEST_SESSION_DAYS * 24 * 60 * 60,
        httponly=True,
        samesite='lax',
        secure=False,
    )


def clear_access_cookie(response: Response) -> None:
    response.delete_cookie(key=ACCESS_COOKIE_NAME, httponly=True, samesite='lax')
