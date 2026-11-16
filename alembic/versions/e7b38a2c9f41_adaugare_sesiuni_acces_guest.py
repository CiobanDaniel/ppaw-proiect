"""Adaugare sesiuni acces pentru vizitatori guest si autentificati.

Revision ID: e7b38a2c9f41
Revises: d4f563a12b9e
Create Date: 2026-11-16
"""

from alembic import op
import sqlalchemy as sa


revision = 'e7b38a2c9f41'
down_revision = 'd4f563a12b9e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'sesiuni_acces',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('token_hash', sa.String(length=64), nullable=False),
        sa.Column('id_utilizator', sa.Integer(), nullable=True),
        sa.Column('data_crearii', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('data_ultima_activitate', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('expira_la', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revocata_la', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint('expira_la IS NULL OR expira_la > data_crearii', name='sesiuni_acces_expirare_check'),
        sa.ForeignKeyConstraint(['id_utilizator'], ['utilizatori.id'], name='sesiuni_acces_id_utilizator_fkey', ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name='sesiuni_acces_pkey'),
        sa.UniqueConstraint('token_hash', name='sesiuni_acces_token_hash_key'),
    )
    op.create_index('ix_sesiuni_acces_utilizator_activitate', 'sesiuni_acces', ['id_utilizator', 'data_ultima_activitate'])
    op.add_column('vizualizari_capitole', sa.Column('id_sesiune_acces', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'vizualizari_capitole_id_sesiune_acces_fkey', 'vizualizari_capitole', 'sesiuni_acces', ['id_sesiune_acces'], ['id'], ondelete='SET NULL'
    )
    op.create_index('ix_vizualizari_capitole_sesiune', 'vizualizari_capitole', ['id_sesiune_acces'])


def downgrade() -> None:
    op.drop_index('ix_vizualizari_capitole_sesiune', table_name='vizualizari_capitole')
    op.drop_constraint('vizualizari_capitole_id_sesiune_acces_fkey', 'vizualizari_capitole', type_='foreignkey')
    op.drop_column('vizualizari_capitole', 'id_sesiune_acces')
    op.drop_index('ix_sesiuni_acces_utilizator_activitate', table_name='sesiuni_acces')
    op.drop_table('sesiuni_acces')
