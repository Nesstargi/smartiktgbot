# backend/repositories/user_repo.py

from sqlalchemy.orm import Session
from backend.models.user import User


def get_user_by_email(db: Session, email: str):
    """
    Получить пользователя по email.
    """
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, email: str, password_hash: str):
    """
    Создать нового пользователя.
    """
    user = User(email=email, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
