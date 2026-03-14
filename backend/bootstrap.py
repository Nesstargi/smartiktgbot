from sqlalchemy import inspect

from backend.database import SessionLocal, engine
from backend.models.role import Role
from backend.models.user_role import UserRole


REQUIRED_TABLES = {"roles", "user_roles"}


def _schema_ready() -> bool:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    return REQUIRED_TABLES.issubset(table_names)


def bootstrap_default_roles():
    if not _schema_ready():
        return

    db = SessionLocal()
    try:
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            admin_role = Role(name="admin")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)

        super_admin_role = db.query(Role).filter(Role.name == "super_admin").first()
        if not super_admin_role:
            super_admin_role = Role(name="super_admin")
            db.add(super_admin_role)
            db.commit()
            db.refresh(super_admin_role)

        has_super_admin = (
            db.query(UserRole)
            .filter(UserRole.role_id == super_admin_role.id)
            .first()
        )
        if has_super_admin:
            return

        first_admin = (
            db.query(UserRole)
            .filter(UserRole.role_id == admin_role.id)
            .order_by(UserRole.user_id.asc())
            .first()
        )
        if first_admin:
            db.add(UserRole(user_id=first_admin.user_id, role_id=super_admin_role.id))
            db.commit()
    finally:
        db.close()
