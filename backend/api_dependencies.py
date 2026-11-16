"""Dependențe reutilizabile de routerele FastAPI."""

from collections.abc import Generator

from sqlalchemy.orm import Session

try:
    from .crud import SessionLocal
except ImportError:
    from crud import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
