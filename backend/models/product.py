from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    description = Column(String, nullable=True)  # краткие характеристики
    image_file_id = Column(String, nullable=True)  # ✅ Telegram file_id
    subcategory_id = Column(Integer, ForeignKey("subcategories.id", ondelete="CASCADE"))

    subcategory = relationship("SubCategory", back_populates="products")
