import os
import sys
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TEST_DB_PATH = Path(__file__).resolve().parent / ".test_db.sqlite3"

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH.as_posix()}"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["JWT_EXPIRE_MINUTES"] = "60"
os.environ["CORS_ALLOW_ORIGINS"] = "http://testserver"
os.environ["LOGIN_RATE_LIMIT_ATTEMPTS"] = "5"
os.environ["LOGIN_RATE_LIMIT_WINDOW_SECONDS"] = "60"
os.environ["LOGIN_RATE_LIMIT_BLOCK_SECONDS"] = "300"
os.environ["BOT_DELIVERY_MODE"] = "polling"
os.environ["TELEGRAM_WEBHOOK_BASE_URL"] = ""
os.environ["TELEGRAM_WEBHOOK_PATH"] = "/telegram/webhook"
os.environ["TELEGRAM_WEBHOOK_SECRET"] = "test-webhook-secret"

import backend.api.admin.auth as auth_api
from backend.core.security import hash_password
from backend.database import SessionLocal, engine
from backend.main import app
from backend.models.bot_setting import BotSetting
from backend.models.category import Category
from backend.models.lead import Lead
from backend.models.product import Product
from backend.models.promotion import Promotion
from backend.models.role import Role
from backend.models.subcategory import SubCategory
from backend.models.user import User
from backend.models.user_permission import UserPermission
from backend.models.user_role import UserRole


@pytest.fixture(scope="session", autouse=True)
def migrated_db():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    alembic_cfg = Config(str(ROOT / "alembic.ini"))
    command.upgrade(alembic_cfg, "head")
    yield
    engine.dispose()


@pytest.fixture(scope="session")
def client(migrated_db):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def reset_test_state(migrated_db):
    auth_api._attempts.clear()
    auth_api._blocked_until.clear()

    db = SessionLocal()
    try:
        for model in (
            UserPermission,
            UserRole,
            Product,
            SubCategory,
            Category,
            Lead,
            Promotion,
            BotSetting,
            User,
            Role,
        ):
            db.query(model).delete()
        db.commit()
    finally:
        db.close()


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_or_create_role(db, name: str) -> Role:
    role = db.query(Role).filter(Role.name == name).first()
    if role:
        return role

    role = Role(name=name)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@pytest.fixture
def create_user():
    def factory(
        *,
        email: str,
        password: str = "secret123",
        roles: list[str] | None = None,
        permissions: list[str] | None = None,
    ):
        db = SessionLocal()
        try:
            user = User(
                email=email.strip().lower(),
                hashed_password=hash_password(password),
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            for role_name in roles or []:
                role = _get_or_create_role(db, role_name)
                db.add(UserRole(user_id=user.id, role_id=role.id))

            for permission in permissions or []:
                db.add(UserPermission(user_id=user.id, permission=permission))

            db.commit()
            return {
                "id": user.id,
                "email": user.email,
                "password": password,
            }
        finally:
            db.close()

    return factory


@pytest.fixture
def create_super_admin(create_user):
    def factory(
        *,
        email: str = "super@example.com",
        password: str = "secret123",
        permissions: list[str] | None = None,
    ):
        return create_user(
            email=email,
            password=password,
            roles=["admin", "super_admin"],
            permissions=permissions or [],
        )

    return factory


@pytest.fixture
def create_catalog():
    def factory(
        *,
        category_name: str = "Phones",
        subcategory_name: str = "Android",
    ):
        db = SessionLocal()
        try:
            category = Category(name=category_name)
            db.add(category)
            db.commit()
            db.refresh(category)

            subcategory = SubCategory(
                name=subcategory_name,
                category_id=category.id,
            )
            db.add(subcategory)
            db.commit()
            db.refresh(subcategory)

            return {
                "category_id": category.id,
                "subcategory_id": subcategory.id,
            }
        finally:
            db.close()

    return factory


@pytest.fixture
def auth_headers(client):
    def factory(email: str, password: str) -> dict[str, str]:
        response = client.post(
            "/admin/auth/login",
            json={"email": email, "password": password},
        )
        assert response.status_code == 200, response.text
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return factory
