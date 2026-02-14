from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0003_expand_human_text_limit"
down_revision = "0002_add_human_text"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("posts") as batch_op:
        batch_op.alter_column(
            "human_text",
            existing_type=sa.String(length=280),
            type_=sa.Text(),
            existing_nullable=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("posts") as batch_op:
        batch_op.alter_column(
            "human_text",
            existing_type=sa.Text(),
            type_=sa.String(length=280),
            existing_nullable=False,
        )
