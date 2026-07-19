"""catalog metadata checkpoint

Revision ID: 3b0ab9a0a29d
Revises: f1265267888f
Create Date: 2026-07-14 18:34:52.163994
"""

from collections.abc import Sequence


revision: str = "3b0ab9a0a29d"
down_revision: str | None = "f1265267888f"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
