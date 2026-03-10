# backend/core/security.py

from datetime import datetime, timedelta
from jose import jwt
from backend.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from passlib.context import CryptContext


def create_access_token(data: dict):
    """
    Создание JWT токена

    data — payload, который мы хотим зашить в токен
    (например: user_id, role, login и т.д.)
    """

    to_encode = data.copy()

    # Время истечения токена
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Добавляем expiration в payload
    to_encode.update({"exp": expire})

    # Подписываем токен секретным ключом
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return token


def decode_token(token: str):
    """
    Расшифровка JWT токена
    Если подпись неверная или токен истёк → будет exception
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    """Хеширование пароля"""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str):
    """Проверка пароля"""
    return pwd_context.verify(plain, hashed)
