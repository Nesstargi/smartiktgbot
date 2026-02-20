from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    subcategories = relationship(
        "SubCategory", back_populates="category", cascade="all, delete"
    )


class SubCategory(Base):
    __tablename__ = "subcategories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"))

    category = relationship("Category", back_populates="subcategories")
    products = relationship(
        "Product", back_populates="subcategory", cascade="all, delete"
    )


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    description = Column(String, nullable=True)  # краткие характеристики
    image_file_id = Column(String, nullable=True)  # ✅ Telegram file_id
    subcategory_id = Column(Integer, ForeignKey("subcategories.id", ondelete="CASCADE"))

    subcategory = relationship("SubCategory", back_populates="products")


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=False)
    telegram_id = Column(String, nullable=True)
    product = Column(String, nullable=True)
