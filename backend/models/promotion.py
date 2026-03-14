from sqlalchemy import Boolean, Column, Integer, String

from backend.database import Base


class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    image_file_id = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
