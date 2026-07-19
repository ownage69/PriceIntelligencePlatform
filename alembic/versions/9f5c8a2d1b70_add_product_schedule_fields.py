"""add product schedule fields

Revision ID: 9f5c8a2d1b70
Revises: 3b0ab9a0a29d
Create Date: 2026-07-19
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "9f5c8a2d1b70"
down_revision: str | None = "3b0ab9a0a29d"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    if "users" in sa.inspect(bind).get_table_names():
        op.drop_table("users")

    op.add_column(
        "products",
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.add_column(
        "products",
        sa.Column("scrape_interval_minutes", sa.Integer(), server_default=sa.text("60"), nullable=False),
    )
    op.create_check_constraint(
        "ck_products_scrape_interval_minutes_positive",
        "products",
        "scrape_interval_minutes > 0",
    )


def downgrade() -> None:
    op.drop_constraint("ck_products_scrape_interval_minutes_positive", "products", type_="check")
    op.drop_column("products", "scrape_interval_minutes")
    op.drop_column("products", "created_at")
