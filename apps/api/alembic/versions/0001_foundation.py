"""baseline foundation migration

Revision ID: 0001_foundation
Revises:
"""

from typing import Sequence, Union

revision: str = "0001_foundation"
down_revision: Union[str, Sequence[str], None] = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Baseline migration.

    Better Auth manages the authentication tables.
    CareerOS application tables will be introduced in later migrations.
    """
    pass


def downgrade() -> None:
    """No-op baseline migration."""
    pass