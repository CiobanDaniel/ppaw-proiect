"""Configurarea comună a aplicației web."""

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
FRONTEND_DIST_DIR = PROJECT_DIR / 'frontend' / 'dist'
ADMIN_PREFIX = '/admin'
ADMIN_LEGACY_PREFIXES = (
    '/utilizatori', '/carti', '/categorii', '/setari', '/alerte', '/capitole',
    '/recenzii', '/comentarii', '/abonamente', '/evenimente', '/plati',
    '/cereri-retragere', '/rapoarte', '/notificari', '/analitice',
)
