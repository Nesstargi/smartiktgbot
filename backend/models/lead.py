from sqlalchemy import Column, DateTime, Integer, String, func

from backend.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=False)
    telegram_id = Column(String, nullable=True)
    product = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
