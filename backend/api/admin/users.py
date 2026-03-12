from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.core.deps import ALL_PERMISSIONS, require_super_admin
from backend.core.security import hash_password
from backend.database import get_db
from backend.models.role import Role
from backend.models.user import User
from backend.models.user_permission import UserPermission
from backend.models.user_role import UserRole
from backend.schemas.admin_user import (
    AdminUserCreate,
    AdminUserOut,
    AdminUserPermissionsUpdate,
    AdminUserRoleUpdate,
)

router = APIRouter()



def _get_or_create_role(db: Session, name: str) -> Role:
    role = db.query(Role).filter(Role.name == name).first()
    if role:
        return role

    role = Role(name=name)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role



def _user_to_out(user: User) -> AdminUserOut:
    return AdminUserOut(
        id=user.id,
        email=user.email,
        is_active=bool(user.is_active),
        roles=[ur.role.name for ur in user.roles if ur.role],
        permissions=[up.permission for up in user.permissions],
    )



def _validate_permissions(permissions: list[str]):
    invalid = [p for p in permissions if p not in ALL_PERMISSIONS]
    if invalid:
        raise HTTPException(status_code=400, detail=f"Unknown permissions: {', '.join(invalid)}")


@router.get("/permissions")
def list_permissions(admin=Depends(require_super_admin)):
    return {"permissions": ALL_PERMISSIONS}


@router.get("/", response_model=list[AdminUserOut])
def list_users(
    db: Session = Depends(get_db),
    admin=Depends(require_super_admin),
):
    users = db.query(User).order_by(User.id.asc()).all()
    return [_user_to_out(u) for u in users]


@router.post("/", response_model=AdminUserOut)
def create_user(
    data: AdminUserCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_super_admin),
):
    _validate_permissions(data.permissions)

    normalized_email = data.email.strip().lower()

    existing = db.query(User).filter(func.lower(User.email) == normalized_email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(email=normalized_email, hashed_password=hash_password(data.password), is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)

    admin_role = _get_or_create_role(db, "admin")
    super_admin_role = _get_or_create_role(db, "super_admin")

    db.add(UserRole(user_id=user.id, role_id=admin_role.id))
    if data.is_super_admin:
        db.add(UserRole(user_id=user.id, role_id=super_admin_role.id))

    for permission in data.permissions:
        db.add(UserPermission(user_id=user.id, permission=permission))

    db.commit()
    db.refresh(user)
    return _user_to_out(user)


@router.put("/{user_id}/permissions", response_model=AdminUserOut)
def update_user_permissions(
    user_id: int,
    data: AdminUserPermissionsUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_super_admin),
):
    _validate_permissions(data.permissions)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.query(UserPermission).filter(UserPermission.user_id == user.id).delete()
    for permission in data.permissions:
        db.add(UserPermission(user_id=user.id, permission=permission))

    db.commit()
    db.refresh(user)
    return _user_to_out(user)


@router.put("/{user_id}/role", response_model=AdminUserOut)
def update_user_super_admin_role(
    user_id: int,
    data: AdminUserRoleUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_super_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    admin_role = _get_or_create_role(db, "admin")
    super_admin_role = _get_or_create_role(db, "super_admin")

    has_admin = any(ur.role_id == admin_role.id for ur in user.roles)
    if not has_admin:
        db.add(UserRole(user_id=user.id, role_id=admin_role.id))

    user_role_row = (
        db.query(UserRole)
        .filter(UserRole.user_id == user.id, UserRole.role_id == super_admin_role.id)
        .first()
    )

    if data.is_super_admin and not user_role_row:
        db.add(UserRole(user_id=user.id, role_id=super_admin_role.id))

    if not data.is_super_admin and user_role_row:
        db.delete(user_role_row)

    db.commit()
    db.refresh(user)
    return _user_to_out(user)


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_super_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"status": "deleted"}
