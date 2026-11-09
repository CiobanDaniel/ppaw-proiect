"""Audit pentru operațiuni financiare de administrare.

Revision ID: c8d452e97f10
Revises: a235ea114181
Create Date: 2026-11-09
"""

from alembic import op
import sqlalchemy as sa


revision = "c8d452e97f10"
down_revision = "a235ea114181"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("plati", sa.Column("id_admin_rambursare", sa.Integer(), nullable=True))
    op.add_column("plati", sa.Column("motiv_rambursare", sa.Text(), nullable=True))
    op.add_column("plati", sa.Column("data_rambursarii", sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key(
        "plati_id_admin_rambursare_fkey", "plati", "utilizatori", ["id_admin_rambursare"], ["id"], ondelete="SET NULL"
    )
    op.add_column("cereri_retragere", sa.Column("id_admin_procesare", sa.Integer(), nullable=True))
    op.add_column("cereri_retragere", sa.Column("observatii_procesare", sa.Text(), nullable=True))
    op.create_foreign_key(
        "cereri_retragere_id_admin_procesare_fkey", "cereri_retragere", "utilizatori", ["id_admin_procesare"], ["id"], ondelete="SET NULL"
    )


def downgrade() -> None:
    op.drop_constraint("cereri_retragere_id_admin_procesare_fkey", "cereri_retragere", type_="foreignkey")
    op.drop_column("cereri_retragere", "observatii_procesare")
    op.drop_column("cereri_retragere", "id_admin_procesare")
    op.drop_constraint("plati_id_admin_rambursare_fkey", "plati", type_="foreignkey")
    op.drop_column("plati", "data_rambursarii")
    op.drop_column("plati", "motiv_rambursare")
    op.drop_column("plati", "id_admin_rambursare")
