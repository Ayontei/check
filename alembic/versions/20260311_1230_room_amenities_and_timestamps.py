"""room amenities and timestamps

Revision ID: 20260311_1230
Revises: 20260311_1202
Create Date: 2026-03-11
"""

from alembic import op
import sqlalchemy as sa


revision = "20260311_1230"
down_revision = "20260311_1202"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No-op: полная схема уже в 20260311_1202
    pass


def downgrade() -> None:
    pass

