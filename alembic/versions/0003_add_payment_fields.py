"""add payment fields to ads

Revision ID: 0003_add_payment_fields
Revises: 0002_add_user_banned
Create Date: 2026-01-15 00:25:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0003_add_payment_fields'
down_revision = '0002_add_user_banned'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('ads', sa.Column('price', sa.Integer(), nullable=True))
    op.add_column('ads', sa.Column('is_paid', sa.Boolean(), nullable=True, server_default=sa.false()))
    op.add_column('ads', sa.Column('payment_id', sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column('ads', 'payment_id')
    op.drop_column('ads', 'is_paid')
    op.drop_column('ads', 'price')
