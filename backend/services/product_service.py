from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.product import Product
from backend.models.subcategory import SubCategory
from backend.repositories.product_repo import ProductRepository
from backend.schemas.product import ProductCreate, ProductUpdate


class ProductService:
    @staticmethod
    def _get_subcategory_or_404(db: Session, subcategory_id: int):
        subcategory = (
            db.query(SubCategory).filter(SubCategory.id == subcategory_id).first()
        )
        if not subcategory:
            raise HTTPException(status_code=404, detail="Subcategory not found")
        return subcategory

    @staticmethod
    def _find_duplicate(db: Session, *, subcategory_id: int, name: str):
        return (
            db.query(Product)
            .filter(
                Product.subcategory_id == subcategory_id,
                func.lower(Product.name) == name.lower(),
            )
            .first()
        )

    @staticmethod
    def create_product(db: Session, data: ProductCreate):
        payload = data.model_dump()
        ProductService._get_subcategory_or_404(db, payload["subcategory_id"])
        existing = ProductService._find_duplicate(
            db,
            subcategory_id=payload["subcategory_id"],
            name=payload["name"],
        )
        if existing:
            raise HTTPException(
                status_code=409,
                detail="Product with this name already exists in this subcategory",
            )

        product = Product(**payload)
        return ProductRepository.create(db, product)

    @staticmethod
    def list_products(db: Session):
        return ProductRepository.get_all(db)

    @staticmethod
    def update_product(db: Session, product_id: int, data: ProductUpdate):
        product = ProductRepository.get_by_id(db, product_id)
        if not product:
            return None

        payload = data.model_dump(exclude_unset=True)
        if "name" in payload:
            existing = ProductService._find_duplicate(
                db,
                subcategory_id=product.subcategory_id,
                name=payload["name"],
            )
            if existing and existing.id != product_id:
                raise HTTPException(
                    status_code=409,
                    detail="Product with this name already exists in this subcategory",
                )

        for key, value in payload.items():
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
