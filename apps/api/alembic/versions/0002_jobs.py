"""create jobs table

Revision ID: 0002_jobs
Revises: 0001_foundation
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0002_jobs"
down_revision: Union[str, Sequence[str], None] = "0001_foundation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


job_status = postgresql.ENUM(
    "saved",
    "applied",
    "interview",
    "offer",
    "rejected",
    "withdrawn",
    name="job_status",
)


def upgrade() -> None:
    job_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "job",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.Text(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "saved",
                "applied",
                "interview",
                "offer",
                "rejected",
                "withdrawn",
                name="job_status",
                create_type=False,
            ),
            server_default="saved",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_job_user_id", "job", ["user_id"])
    op.create_index("ix_job_status", "job", ["status"])


def downgrade() -> None:
    op.drop_index("ix_job_status", table_name="job")
    op.drop_index("ix_job_user_id", table_name="job")
    op.drop_table("job")
    job_status.drop(op.get_bind(), checkfirst=True)