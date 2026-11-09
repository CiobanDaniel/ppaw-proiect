"""Reguli de integritate pentru formularele administrative.

Revision ID: d4f563a12b9e
Revises: c8d452e97f10
Create Date: 2026-11-09
"""

from alembic import op


revision = "d4f563a12b9e"
down_revision = "c8d452e97f10"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint("unique_book_chapter", "capitole", ["id_carte", "numar_capitol"])
    op.create_check_constraint("capitole_numar_pozitiv_check", "capitole", "numar_capitol >= 1")
    op.create_check_constraint("capitole_cost_pozitiv_check", "capitole", "cost_puncte >= 0")
    op.create_check_constraint("evenimente_recompensa_pozitiva_check", "evenimente_promotionale", "recompensa_puncte >= 0")
    op.create_check_constraint("nivele_pret_pozitiv_check", "nivele_abonament", "pret_real >= 0")
    op.create_check_constraint("cereri_retragere_suma_pozitiva_check", "cereri_retragere", "suma >= 0")
    op.create_check_constraint("plati_suma_pozitiva_check", "plati", "suma_reala >= 0")


def downgrade() -> None:
    op.drop_constraint("plati_suma_pozitiva_check", "plati", type_="check")
    op.drop_constraint("cereri_retragere_suma_pozitiva_check", "cereri_retragere", type_="check")
    op.drop_constraint("nivele_pret_pozitiv_check", "nivele_abonament", type_="check")
    op.drop_constraint("evenimente_recompensa_pozitiva_check", "evenimente_promotionale", type_="check")
    op.drop_constraint("capitole_cost_pozitiv_check", "capitole", type_="check")
    op.drop_constraint("capitole_numar_pozitiv_check", "capitole", type_="check")
    op.drop_constraint("unique_book_chapter", "capitole", type_="unique")
