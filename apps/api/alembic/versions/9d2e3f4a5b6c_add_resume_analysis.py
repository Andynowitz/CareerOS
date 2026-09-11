"""add resume analysis

Revision ID: 9d2e3f4a5b6c
Revises: 8c1d2e3f4a5b
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "9d2e3f4a5b6c"
down_revision: Union[str, Sequence[str], None] = "8c1d2e3f4a5b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "resume_analysis",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("resume_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "skills",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("experience_summary", sa.Text(), nullable=True),
        sa.Column("education_summary", sa.Text(), nullable=True),
        sa.Column("projects_summary", sa.Text(), nullable=True),
        sa.Column(
            "raw_analysis",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["resume_id"],
            ["resume.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_resume_analysis_resume_id",
        "resume_analysis",
        ["resume_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_resume_analysis_resume_id", table_name="resume_analysis")
    op.drop_table("resume_analysis")
