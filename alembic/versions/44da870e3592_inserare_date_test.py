"""Inserare_Date_Test

Revision ID: 44da870e3592
Revises: 57d9c7b75021
Create Date: 2026-10-19 18:29:11.600798

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision: str = '44da870e3592'
down_revision: Union[str, Sequence[str], None] = '57d9c7b75021'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Inseram mai intai in 'utilizatori' (tabelul parinte)
    op.execute(text("""
        INSERT INTO utilizatori (nume_utilizator, email, parola_hash, rol, puncte)
        VALUES ('autor_seed', 'autor_seed@test.ro', 'hash_test_123', 'autor', 100);
    """))

    # 2. Inseram in 'carti' (tabelul copil, care depinde de id_autor)
    op.execute(text("""
        INSERT INTO carti (titlu, descriere, stare, id_autor)
        VALUES ('Arhitectura Code First', 'Ghid complet pentru migrari ORM.', 'publicat', 
                (SELECT id FROM utilizatori WHERE email = 'autor_seed@test.ro'));
    """))

def downgrade() -> None:
    # Stergem in ordine inversa pentru a nu incalca restrictiile FK
    op.execute(text("DELETE FROM carti WHERE titlu = 'Arhitectura Code First';"))
    op.execute(text("DELETE FROM utilizatori WHERE email = 'autor_seed@test.ro';"))
