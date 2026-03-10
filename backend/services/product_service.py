from sqlalchemy.orm import Session
from backend.models.product import Product
from backend.repositories.product_repo import ProductRepository
from backend.schemas.product import ProductCreate, ProductUpdate


class ProductService:

    @staticmethod
    def create_product(db: Session, data: ProductCreate):
        product = Product(**data.dict())
        return ProductRepository.create(db, product)

    @staticmethod
    def list_products(db: Session):
        return ProductRepository.get_all(db)

    @staticmethod
    def update_product(db: Session, product_id: int, data: ProductUpdate):
        product = ProductRepository.get_by_id(db, product_id)
        if not product:
            return None

        for key, value in data.dict(exclude_unset=True).items():
            setattr(product, key, value)

        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def delete_product(db: Session, product_id: int):
        product = ProductRepository.get_by_id(db, product_id)
        if not product:
            return False

        ProductRepository.delete(db, product)
        return True
