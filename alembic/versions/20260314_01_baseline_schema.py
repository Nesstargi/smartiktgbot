"""baseline schema

Revision ID: 20260314_01
Revises:
Create Date: 2026-03-14 00:00:00

"""

from typing import Iterable

from alembic import op
import sqlalchemy as sa


revision = "20260314_01"
down_revision = None
branch_labels = None
depends_on = None

DEFAULT_START_MESSAGE = "Welcome! Choose a menu option."
DEFAULT_REMINDER = (
    "Вы смотрели товары, но не оставили заявку. Ответьте на это сообщение, "
    "и мы поможем оформить заказ."
)
DEFAULT_CONSULTATION_PHONE = "+7 (000) 000-00-00"
DEFAULT_CONSULTATION_MESSAGE = (
    "📞 Для консультации позвоните по номеру: {phone}\n\n"
    "✍️ Или задайте вопрос в сообщении ниже."
)
DEFAULT_CONSULTATION_CONTACT_PROMPT = (
    "Спасибо, вопрос получил. Теперь нажмите кнопку ниже и поделитесь номером телефона:"
)
DEFAULT_ABOUT_MESSAGE = (
    "О компании: мы помогаем подобрать решение под ваш запрос."
)


def _string_default(value: str):
    escaped = value.replace("'", "''")
    return sa.text(f"'{escaped}'")


def _column_names(bind, table_name: str) -> set[str]:
    inspector = sa.inspect(bind)
    return {column["name"] for column in inspector.get_columns(table_name)}


def _table_names(bind) -> set[str]:
    inspector = sa.inspect(bind)
    return set(inspector.get_table_names())


def _has_unique_columns(bind, table_name: str, columns: Iterable[str]) -> bool:
    inspector = sa.inspect(bind)
    expected = tuple(columns)

    for index in inspector.get_indexes(table_name):
        if index.get("unique") and tuple(index.get("column_names") or []) == expected:
            return True

    try:
        unique_constraints = inspector.get_unique_constraints(table_name)
    except NotImplementedError:
        unique_constraints = []

    for constraint in unique_constraints:
        if tuple(constraint.get("column_names") or []) == expected:
            return True

    return False


def _create_unique_index_if_missing(
    bind,
    table_name: str,
    index_name: str,
    columns: list[str],
):
    inspector = sa.inspect(bind)
    existing_indexes = {index["name"] for index in inspector.get_indexes(table_name)}
    if index_name in existing_indexes or _has_unique_columns(bind, table_name, columns):
        return
    op.create_index(index_name, table_name, columns, unique=True)


def upgrade():
    bind = op.get_bind()
    tables = _table_names(bind)

    if "categories" not in tables:
        op.create_table(
            "categories",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(), nullable=False),
        )

    if "roles" not in tables:
        op.create_table(
            "roles",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(), nullable=True),
        )

    if "users" not in tables:
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("email", sa.String(), nullable=True),
            sa.Column("hashed_password", sa.String(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.true()),
        )

    if "bot_settings" not in tables:
        op.create_table(
            "bot_settings",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "start_message",
                sa.String(),
                nullable=False,
                server_default=_string_default(DEFAULT_START_MESSAGE),
            ),
            sa.Column(
                "abandoned_reminder_message",
                sa.String(),
                nullable=False,
                server_default=_string_default(DEFAULT_REMINDER),
            ),
            sa.Column(
                "abandoned_reminder_delay_minutes",
                sa.Integer(),
                nullable=False,
                server_default=sa.text("30"),
            ),
            sa.Column(
                "consultation_phone",
                sa.String(),
                nullable=False,
                server_default=_string_default(DEFAULT_CONSULTATION_PHONE),
            ),
            sa.Column(
                "consultation_message",
                sa.String(),
                nullable=False,
                server_default=_string_default(DEFAULT_CONSULTATION_MESSAGE),
            ),
            sa.Column(
                "consultation_contact_prompt",
                sa.String(),
                nullable=False,
                server_default=_string_default(DEFAULT_CONSULTATION_CONTACT_PROMPT),
            ),
            sa.Column(
                "about_message",
                sa.String(),
                nullable=False,
                server_default=_string_default(DEFAULT_ABOUT_MESSAGE),
            ),
        )

    if "promotions" not in tables:
        op.create_table(
            "promotions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("title", sa.String(), nullable=False),
            sa.Column("description", sa.String(), nullable=True),
            sa.Column("image_url", sa.String(), nullable=True),
            sa.Column("image_file_id", sa.String(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        )

    if "leads" not in tables:
        op.create_table(
            "leads",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(), nullable=True),
            sa.Column("phone", sa.String(), nullable=False),
            sa.Column("telegram_id", sa.String(), nullable=True),
            sa.Column("product", sa.String(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.now(),
            ),
        )

    if "subcategories" not in tables:
        op.create_table(
            "subcategories",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(), nullable=False),
            sa.Column("image_url", sa.String(), nullable=True),
            sa.Column(
                "category_id",
                sa.Integer(),
                sa.ForeignKey("categories.id", ondelete="CASCADE"),
                nullable=True,
            ),
        )

    if "products" not in tables:
        op.create_table(
            "products",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(), nullable=False),
            sa.Column("description", sa.String(), nullable=True),
            sa.Column("image_file_id", sa.String(), nullable=True),
            sa.Column(
                "subcategory_id",
                sa.Integer(),
                sa.ForeignKey("subcategories.id", ondelete="CASCADE"),
                nullable=True,
            ),
        )

    if "user_roles" not in tables:
        op.create_table(
            "user_roles",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id"), nullable=True),
        )

    if "user_permissions" not in tables:
        op.create_table(
            "user_permissions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("permission", sa.String(), nullable=False),
        )

    _create_unique_index_if_missing(bind, "categories", "uq_categories_name", ["name"])
    _create_unique_index_if_missing(bind, "roles", "uq_roles_name", ["name"])
    _create_unique_index_if_missing(bind, "users", "ix_users_email", ["email"])
    _create_unique_index_if_missing(
        bind,
        "user_permissions",
        "uq_user_permissions_user_id_permission",
        ["user_id", "permission"],
    )

    product_columns = _column_names(bind, "products")
    if "description" not in product_columns:
        op.add_column("products", sa.Column("description", sa.String(), nullable=True))
    if "image_file_id" not in product_columns:
        op.add_column("products", sa.Column("image_file_id", sa.String(), nullable=True))

    subcategory_columns = _column_names(bind, "subcategories")
    if "image_url" not in subcategory_columns:
        op.add_column("subcategories", sa.Column("image_url", sa.String(), nullable=True))

    promotion_columns = _column_names(bind, "promotions")
    if "image_url" not in promotion_columns:
        op.add_column("promotions", sa.Column("image_url", sa.String(), nullable=True))
    if "image_file_id" not in promotion_columns:
        op.add_column("promotions", sa.Column("image_file_id", sa.String(), nullable=True))
    if "is_active" not in promotion_columns:
        op.add_column(
            "promotions",
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        )

    bot_settings_columns = _column_names(bind, "bot_settings")
    if "start_message" not in bot_settings_columns:
        op.add_column(
            "bot_settings",
            sa.Column(
                "start_message",
                sa.String(),
                nullable=False,
                server_default=_string_default(DEFAULT_START_MESSAGE),
            ),
        )
    if "abandoned_reminder_message" not in bot_settings_columns:
        op.add_column(
            "bot_settings",
            sa.Column(
                "abandoned_reminder_message",
                sa.String(),
                nullable=False,
                server_default=_string_default(DEFAULT_REMINDER),
            ),
        )
    if "abandoned_reminder_delay_minutes" not in bot_settings_columns:
        op.add_column(
            "bot_settings",
            sa.Column(
                "abandoned_reminder_delay_minutes",
                sa.Integer(),
                nullable=False,
                server_default=sa.text("30"),
            ),
        )
    if "consultation_phone" not in bot_settings_columns:
        op.add_column(
            "bot_settings",
            sa.Column(
                "consultation_phone",
                sa.String(),
                nullable=False,
                server_default=_string_default(DEFAULT_CONSULTATION_PHONE),
            ),
        )
    if "consultation_message" not in bot_settings_columns:
        op.add_column(
            "bot_settings",
            sa.Column(
                "consultation_message",
                sa.String(),
                nullable=False,
                server_default=_string_default(DEFAULT_CONSULTATION_MESSAGE),
            ),
        )
    if "consultation_contact_prompt" not in bot_settings_columns:
        op.add_column(
            "bot_settings",
            sa.Column(
                "consultation_contact_prompt",
                sa.String(),
                nullable=False,
                server_default=_string_default(DEFAULT_CONSULTATION_CONTACT_PROMPT),
            ),
        )
    if "about_message" not in bot_settings_columns:
        op.add_column(
            "bot_settings",
            sa.Column(
                "about_message",
                sa.String(),
                nullable=False,
                server_default=_string_default(DEFAULT_ABOUT_MESSAGE),
            ),
        )

    lead_columns = _column_names(bind, "leads")
    if "created_at" not in lead_columns:
        if bind.dialect.name == "sqlite":
            op.add_column(
                "leads",
                sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            )
            op.execute(
                sa.text(
                    "UPDATE leads SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"
                )
            )
        else:
            op.add_column(
                "leads",
                sa.Column(
                    "created_at",
                    sa.DateTime(timezone=True),
                    nullable=False,
                    server_default=sa.func.now(),
                ),
            )


def downgrade():
    bind = op.get_bind()
    tables = _table_names(bind)

    for table_name in [
        "user_permissions",
        "user_roles",
        "products",
        "subcategories",
        "leads",
        "promotions",
        "bot_settings",
        "users",
        "roles",
        "categories",
    ]:
        if table_name in tables:
            op.drop_table(table_name)
