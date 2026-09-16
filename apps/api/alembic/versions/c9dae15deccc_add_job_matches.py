"""add job matches

Revision ID: c9dae15deccc
Revises: 9d2e3f4a5b6c
Create Date: 2026-09-14 09:06:51.420645

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "c9dae15deccc"
down_revision: Union[str, Sequence[str], None] = "9d2e3f4a5b6c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "job_matches",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "job_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "resume_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "score",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "required_skills_score",
            sa.Float(),
            nullable=False,
        ),
        sa.Column(
            "preferred_skills_score",
            sa.Float(),
            nullable=False,
        ),
        sa.Column(
            "experience_score",
            sa.Float(),
            nullable=False,
        ),
        sa.Column(
            "education_score",
            sa.Float(),
            nullable=False,
        ),
        sa.Column(
            "keywords_score",
            sa.Float(),
            nullable=False,
        ),
        sa.Column(
            "matched_required_skills",
            postgresql.JSONB(),
            nullable=False,
        ),
        sa.Column(
            "missing_required_skills",
            postgresql.JSONB(),
            nullable=False,
        ),
        sa.Column(
            "matched_preferred_skills",
            postgresql.JSONB(),
            nullable=False,
        ),
        sa.Column(
            "missing_preferred_skills",
            postgresql.JSONB(),
            nullable=False,
        ),
        sa.Column(
            "explanations",
            postgresql.JSONB(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["job_id"],
            ["job.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["resume_id"],
            ["resume.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_job_matches_job_id",
        "job_matches",
        ["job_id"],
    )

    op.create_index(
        "ix_job_matches_resume_id",
        "job_matches",
        ["resume_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_job_matches_resume_id",
        table_name="job_matches",
    )

    op.drop_index(
        "ix_job_matches_job_id",
        table_name="job_matches",
    )

    op.drop_table("job_matches")