"""Adaugare steag pentru stergerea logica a entitatilor cu istoric.

Revision ID: f19a4c27d8b2
Revises: e7b38a2c9f41
Create Date: 2026-11-20
"""

from alembic import op
import sqlalchemy as sa


revision = 'f19a4c27d8b2'
down_revision = 'e7b38a2c9f41'
branch_labels = None
depends_on = None


def upgrade() -> None:
    for table_name in ('utilizatori', 'carti', 'capitole', 'nivele_abonament'):
        op.add_column(
            table_name,
            sa.Column('este_sters', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        )


def downgrade() -> None:
    for table_name in ('nivele_abonament', 'capitole', 'carti', 'utilizatori'):
        op.drop_column(table_name, 'este_sters')
