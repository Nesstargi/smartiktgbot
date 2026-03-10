from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    users = relationship("UserRole", back_populates="role")
