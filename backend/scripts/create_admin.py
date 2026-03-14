import argparse
import os
import sys
from pathlib import Path

from sqlalchemy import func
from sqlalchemy.exc import OperationalError

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.core.deps import ALL_PERMISSIONS
from backend.core.security import hash_password
from backend.database import SessionLocal
from backend.models.role import Role
from backend.models.user import User
from backend.models.user_permission import UserPermission
from backend.models.user_role import UserRole


def parse_args():
    parser = argparse.ArgumentParser(description="Create a super admin user.")
    parser.add_argument("--email", default=os.getenv("ADMIN_EMAIL"))
    parser.add_argument("--password", default=os.getenv("ADMIN_PASSWORD"))
    return parser.parse_args()


def get_or_create_role(db, name: str) -> Role:
    role = db.query(Role).filter(Role.name == name).first()
    if role:
        return role

    role = Role(name=name)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def main():
    args = parse_args()
    email = (args.email or "").strip().lower()
    password = args.password or ""

    if not email or not password:
        raise SystemExit(
            "Email and password are required. Pass --email/--password or set ADMIN_EMAIL/ADMIN_PASSWORD."
        )

    db = SessionLocal()
    try:
        existing = db.query(User).filter(func.lower(User.email) == email).first()
        if existing:
            raise SystemExit(f"User already exists: {email}")

        user = User(email=email, hashed_password=hash_password(password), is_active=True)
        db.add(user)
        db.commit()
        db.refresh(user)

        admin_role = get_or_create_role(db, "admin")
        super_role = get_or_create_role(db, "super_admin")

        db.add(UserRole(user_id=user.id, role_id=admin_role.id))
        db.add(UserRole(user_id=user.id, role_id=super_role.id))

        for permission in ALL_PERMISSIONS:
            db.add(UserPermission(user_id=user.id, permission=permission))

        db.commit()
    except OperationalError as exc:
        raise SystemExit(
            "Database schema is not ready. Run 'alembic upgrade head' first."
        ) from exc
    finally:
        db.close()

    print(f"Super admin created: {email}")


if __name__ == "__main__":
    main()
