from fastapi import Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session

from backend.core.jwt import decode_token, oauth2_scheme
from backend.database import get_db
from backend.models.user import User

PERMISSION_MANAGE_CATEGORIES = "manage_categories"
PERMISSION_MANAGE_SUBCATEGORIES = "manage_subcategories"
PERMISSION_MANAGE_PRODUCTS = "manage_products"
PERMISSION_MANAGE_PROMOTIONS = "manage_promotions"
PERMISSION_MANAGE_BOT_SETTINGS = "manage_bot_settings"
PERMISSION_MANAGE_USERS = "manage_users"
PERMISSION_MANAGE_NOTIFICATIONS = "manage_notifications"
PERMISSION_MANAGE_CONSULTATION = "manage_consultation"
PERMISSION_MANAGE_ABOUT = "manage_about"
PERMISSION_MANAGE_LEADS = "manage_leads"

ALL_PERMISSIONS = [
    PERMISSION_MANAGE_CATEGORIES,
    PERMISSION_MANAGE_SUBCATEGORIES,
    PERMISSION_MANAGE_PRODUCTS,
    PERMISSION_MANAGE_PROMOTIONS,
    PERMISSION_MANAGE_BOT_SETTINGS,
    PERMISSION_MANAGE_USERS,
    PERMISSION_MANAGE_NOTIFICATIONS,
    PERMISSION_MANAGE_CONSULTATION,
    PERMISSION_MANAGE_ABOUT,
    PERMISSION_MANAGE_LEADS,
]


def get_current_admin(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_token(token)

        roles = payload.get("roles") or []
        single_role = payload.get("role")
        if single_role and single_role not in roles:
            roles.append(single_role)

        if "admin" not in roles and "super_admin" not in roles:
            raise HTTPException(status_code=403, detail="Not authorized")

        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    payload = decode_token(token)
    raw_user_id = payload.get("user_id") or payload.get("sub")

    if raw_user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(User).filter(User.id == int(raw_user_id)).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def _get_roles_and_permissions(user: User):
    roles = [ur.role.name for ur in user.roles if ur.role]
    permissions = [up.permission for up in user.permissions]
    return roles, permissions


def require_role(role_name: str):
    def checker(user=Depends(get_current_user)):
        roles, _ = _get_roles_and_permissions(user)
        if role_name not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user

    return checker


def require_super_admin(user=Depends(get_current_user)):
    roles, _ = _get_roles_and_permissions(user)
    if "super_admin" not in roles:
        raise HTTPException(status_code=403, detail="Super admin only")
    return user


def require_permission(permission: str):
    def checker(user=Depends(get_current_user)):
        roles, permissions = _get_roles_and_permissions(user)
        if "super_admin" in roles:
            return user

        if permission not in permissions:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        return user

    return checker


def require_any_permission(permissions: list[str]):
    def checker(user=Depends(get_current_user)):
        roles, user_permissions = _get_roles_and_permissions(user)
        if "super_admin" in roles:
            return user

        if not any(item in user_permissions for item in permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        return user

    return checker
