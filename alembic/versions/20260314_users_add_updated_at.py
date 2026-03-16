"""add updated_at to users

Revision ID: 20260314_users
Revises: 20260311_1202
Create Date: 2026-03-14

"""
from alembic import op
import sqlalchemy as sa


revision = "20260314_users"
down_revision = "20260311_1202"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("users", "updated_at")
