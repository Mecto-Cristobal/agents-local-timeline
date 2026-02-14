from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("color", sa.String(length=20), nullable=False),
        sa.Column("settings_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_accounts_name", "accounts", ["name"], unique=True)

    op.create_table(
        "posts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=10), nullable=False),
        sa.Column("job_name", sa.String(length=200), nullable=False),
        sa.Column("env", sa.String(length=100), nullable=False),
        sa.Column("version", sa.String(length=100), nullable=False),
        sa.Column("when_ts", sa.DateTime(), nullable=True),
        sa.Column("goal", sa.Text(), nullable=False),
        sa.Column("result_summary", sa.Text(), nullable=False),
        sa.Column("latency_p95_ms", sa.Float(), nullable=True),
        sa.Column("tokens", sa.Integer(), nullable=True),
        sa.Column("cost_usd", sa.Float(), nullable=True),
        sa.Column("retries", sa.Integer(), nullable=True),
        sa.Column("anomaly_summary", sa.Text(), nullable=False),
        sa.Column("error_summary", sa.Text(), nullable=False),
        sa.Column("data_deps_summary", sa.Text(), nullable=False),
        sa.Column("next_action", sa.Text(), nullable=False),
        sa.Column("tags_csv", sa.String(length=400), nullable=False),
        sa.Column("raw_payload_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
    )
    op.create_index("ix_posts_account_id", "posts", ["account_id"], unique=False)
    op.create_index("ix_posts_created_at", "posts", ["created_at"], unique=False)

    op.create_table(
        "scenes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("scene_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
    )
    op.create_index("ix_scenes_name", "scenes", ["name"], unique=False)

    op.execute(
        """
        CREATE VIRTUAL TABLE posts_fts USING fts5(
          job_name,
          goal,
          result_summary,
          anomaly_summary,
          error_summary,
          data_deps_summary,
          next_action,
          tags_csv,
          content='posts',
          content_rowid='id'
        );
        """
    )
    op.execute(
        """
        CREATE TRIGGER posts_ai AFTER INSERT ON posts BEGIN
          INSERT INTO posts_fts(rowid, job_name, goal, result_summary, anomaly_summary, error_summary, data_deps_summary, next_action, tags_csv)
          VALUES (new.id, new.job_name, new.goal, new.result_summary, new.anomaly_summary, new.error_summary, new.data_deps_summary, new.next_action, new.tags_csv);
        END;
        """
    )
    op.execute(
        """
        CREATE TRIGGER posts_ad AFTER DELETE ON posts BEGIN
          INSERT INTO posts_fts(posts_fts, rowid, job_name, goal, result_summary, anomaly_summary, error_summary, data_deps_summary, next_action, tags_csv)
          VALUES ('delete', old.id, old.job_name, old.goal, old.result_summary, old.anomaly_summary, old.error_summary, old.data_deps_summary, old.next_action, old.tags_csv);
        END;
        """
    )
    op.execute(
        """
        CREATE TRIGGER posts_au AFTER UPDATE ON posts BEGIN
          INSERT INTO posts_fts(posts_fts, rowid, job_name, goal, result_summary, anomaly_summary, error_summary, data_deps_summary, next_action, tags_csv)
          VALUES ('delete', old.id, old.job_name, old.goal, old.result_summary, old.anomaly_summary, old.error_summary, old.data_deps_summary, old.next_action, old.tags_csv);
          INSERT INTO posts_fts(rowid, job_name, goal, result_summary, anomaly_summary, error_summary, data_deps_summary, next_action, tags_csv)
          VALUES (new.id, new.job_name, new.goal, new.result_summary, new.anomaly_summary, new.error_summary, new.data_deps_summary, new.next_action, new.tags_csv);
        END;
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS posts_au")
    op.execute("DROP TRIGGER IF EXISTS posts_ad")
    op.execute("DROP TRIGGER IF EXISTS posts_ai")
    op.execute("DROP TABLE IF EXISTS posts_fts")
    op.drop_index("ix_scenes_name", table_name="scenes")
    op.drop_table("scenes")
    op.drop_index("ix_posts_created_at", table_name="posts")
    op.drop_index("ix_posts_account_id", table_name="posts")
    op.drop_table("posts")
    op.drop_index("ix_accounts_name", table_name="accounts")
    op.drop_table("accounts")
