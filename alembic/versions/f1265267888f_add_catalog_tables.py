"""add catalog tables

Revision ID: f1265267888f
Revises: 4184e4b8a61c
Create Date: 2026-07-13 19:26:20.269120
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "f1265267888f"
down_revision: str | None = "4184e4b8a61c"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "stores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("domain", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("domain"),
    )
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "product_tags",
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("product_id", "tag_id"),
    )
    op.add_column("products", sa.Column("store_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "products", "stores", ["store_id"], ["id"], ondelete="SET NULL")


def downgrade() -> None:
    op.drop_constraint(None, "products", type_="foreignkey")
    op.drop_column("products", "store_id")
    op.drop_table("product_tags")
    op.drop_table("tags")
    op.drop_table("stores")
