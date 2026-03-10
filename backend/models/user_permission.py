from sqlalchemy import Column, Integer, String, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship

from backend.database import Base


class UserPermission(Base):
    __tablename__ = "user_permissions"
    __table_args__ = (UniqueConstraint("user_id", "permission", name="uq_user_permission"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    permission = Column(String, nullable=False)

    user = relationship("User", back_populates="permissions")
