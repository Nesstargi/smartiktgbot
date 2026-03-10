from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    permissions = relationship(
        "UserPermission",
        back_populates="user",
        cascade="all, delete-orphan",
    )
