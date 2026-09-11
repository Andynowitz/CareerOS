"""add resumes and resume versions

Revision ID: 2d3f4a5b6c7d
Revises: 1c060b9ee10d
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "2d3f4a5b6c7d"

down_revision: Union[
    str,
    Sequence[str],
    None
] = "1c060b9ee10d"

branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "resume",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "current_version",
            sa.Integer(),
            server_default="1",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_resume_user_id",
        "resume",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "resume_version",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "resume_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "version",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "filename",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "content_type",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "size_bytes",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "object_key",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "extracted_text",
            sa.Text(),
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
        sa.UniqueConstraint("object_key"),
        sa.UniqueConstraint(
            "resume_id",
            "version",
            name="uq_resume_version_resume_id_version",
        ),
    )

    op.create_index(
        "ix_resume_version_resume_id",
        "resume_version",
        ["resume_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_resume_version_resume_id",
        table_name="resume_version",
    )

    op.drop_table("resume_version")

    op.drop_index(
        "ix_resume_user_id",
        table_name="resume",
    )

    op.drop_table("resume")