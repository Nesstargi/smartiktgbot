from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

    # связь с подкатегориями
    subcategories = relationship(
        "SubCategory", back_populates="category", cascade="all, delete"
    )
