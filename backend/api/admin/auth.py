import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.config import (
    LOGIN_RATE_LIMIT_ATTEMPTS,
    LOGIN_RATE_LIMIT_BLOCK_SECONDS,
    LOGIN_RATE_LIMIT_WINDOW_SECONDS,
)
from backend.core.deps import get_current_user
from backend.core.jwt import create_access_token
from backend.core.security import verify_password
from backend.database import get_db
from backend.models.user import User

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


_attempts: dict[str, deque[float]] = defaultdict(deque)
_blocked_until: dict[str, float] = {}
_lock = Lock()


def _client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _rate_limit_key(request: Request, email: str) -> str:
    return f"{_client_ip(request)}:{email.strip().lower()}"


def _is_blocked(key: str, now: float) -> bool:
    blocked_until = _blocked_until.get(key, 0)
    return blocked_until > now


def _register_failed_attempt(key: str, now: float):
    q = _attempts[key]
    window_start = now - LOGIN_RATE_LIMIT_WINDOW_SECONDS
    while q and q[0] < window_start:
        q.popleft()

    q.append(now)
    if len(q) >= LOGIN_RATE_LIMIT_ATTEMPTS:
        _blocked_until[key] = now + LOGIN_RATE_LIMIT_BLOCK_SECONDS
        q.clear()


def _clear_attempts(key: str):
    _attempts.pop(key, None)
    _blocked_until.pop(key, None)


def _user_roles_permissions(user: User):
    roles = [ur.role.name for ur in user.roles if ur.role]
    permissions = [up.permission for up in user.permissions]
    return roles, permissions


@router.post("/login")
def login(data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    key = _rate_limit_key(request, data.email)
    now = time.monotonic()

    with _lock:
        if _is_blocked(key, now):
            raise HTTPException(
                status_code=429,
                detail="Too many login attempts. Try again later.",
            )

    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.hashed_password):
        with _lock:
            _register_failed_attempt(key, now)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    with _lock:
        _clear_attempts(key)

    roles, permissions = _user_roles_permissions(user)

    token = create_access_token(
        {
            "user_id": user.id,
            "email": user.email,
            "roles": roles,
            "permissions": permissions,
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "roles": roles,
            "permissions": permissions,
        },
    }


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    roles, permissions = _user_roles_permissions(user)
    return {
        "id": user.id,
        "email": user.email,
        "roles": roles,
        "permissions": permissions,
    }
