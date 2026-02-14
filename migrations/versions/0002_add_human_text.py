from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0002_add_human_text"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("posts")}
    if "human_text" not in columns:
        op.add_column(
            "posts",
            sa.Column("human_text", sa.String(length=280), nullable=False, server_default=""),
        )
        op.execute("UPDATE posts SET human_text = ''")
        op.alter_column("posts", "human_text", server_default=None)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("posts")}
    if "human_text" in columns:
        op.drop_column("posts", "human_text")
