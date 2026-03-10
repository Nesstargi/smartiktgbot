from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.database import Base


class SubCategory(Base):
    __tablename__ = "subcategories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    image_url = Column(String, nullable=True)

    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"))

    category = relationship("Category", back_populates="subcategories")
    products = relationship("Product", back_populates="subcategory", cascade="all, delete")
