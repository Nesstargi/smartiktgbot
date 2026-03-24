from sqlalchemy import Column, DateTime, Integer, String, func

from backend.database import Base


class BotSubscriber(Base):
    __tablename__ = "bot_subscribers"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, nullable=False, unique=True, index=True)
    telegram_user_id = Column(String, nullable=True, index=True)
    username = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_seen_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
