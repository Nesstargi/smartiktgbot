from sqlalchemy.orm import Session

from backend.core.jwt import create_access_token
from backend.core.security import verify_password
from backend.repositories.user_repo import get_user_by_email


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    roles = [ur.role.name for ur in user.roles]

    token = create_access_token(
        {
            "user_id": user.id,
            "email": user.email,
            "roles": roles,
        }
    )

    return token
