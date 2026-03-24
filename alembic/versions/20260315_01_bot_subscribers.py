"""add bot subscribers audience table

Revision ID: 20260315_01
Revises: 20260314_01
Create Date: 2026-03-15 00:00:00

"""

from alembic import op
import sqlalchemy as sa


revision = "20260315_01"
down_revision = "20260314_01"
branch_labels = None
depends_on = None


def _table_names(bind) -> set[str]:
    inspector = sa.inspect(bind)
    return set(inspector.get_table_names())


def _column_names(bind, table_name: str) -> set[str]:
    inspector = sa.inspect(bind)
    return {column["name"] for column in inspector.get_columns(table_name)}


def _index_names(bind, table_name: str) -> set[str]:
    inspector = sa.inspect(bind)
    return {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade():
    bind = op.get_bind()
    tables = _table_names(bind)

    if "bot_subscribers" not in tables:
        op.create_table(
            "bot_subscribers",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("chat_id", sa.String(), nullable=False),
            sa.Column("telegram_user_id", sa.String(), nullable=True),
            sa.Column("username", sa.String(), nullable=True),
            sa.Column("full_name", sa.String(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.now(),
            ),
            sa.Column(
                "last_seen_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.now(),
            ),
        )

    columns = _column_names(bind, "bot_subscribers")
    if "telegram_user_id" not in columns:
        op.add_column("bot_subscribers", sa.Column("telegram_user_id", sa.String(), nullable=True))
    if "username" not in columns:
        op.add_column("bot_subscribers", sa.Column("username", sa.String(), nullable=True))
    if "full_name" not in columns:
        op.add_column("bot_subscribers", sa.Column("full_name", sa.String(), nullable=True))
    if "created_at" not in columns:
        op.add_column(
            "bot_subscribers",
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.now(),
            ),
        )
    if "last_seen_at" not in columns:
        op.add_column(
            "bot_subscribers",
            sa.Column(
                "last_seen_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.now(),
            ),
        )

    indexes = _index_names(bind, "bot_subscribers")
    if "ix_bot_subscribers_chat_id" not in indexes:
        op.create_index("ix_bot_subscribers_chat_id", "bot_subscribers", ["chat_id"], unique=True)
    if "ix_bot_subscribers_telegram_user_id" not in indexes:
        op.create_index(
            "ix_bot_subscribers_telegram_user_id",
            "bot_subscribers",
            ["telegram_user_id"],
            unique=False,
        )


def downgrade():
    bind = op.get_bind()
    if "bot_subscribers" in _table_names(bind):
        op.drop_table("bot_subscribers")
