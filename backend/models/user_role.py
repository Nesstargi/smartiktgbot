from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    role_id = Column(Integer, ForeignKey("roles.id"))

    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")
