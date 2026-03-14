from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.category import Category
from backend.repositories.category_repo import CategoryRepository
from backend.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    @staticmethod
    def _find_by_normalized_name(db: Session, name: str):
        return db.query(Category).filter(func.lower(Category.name) == name.lower()).first()

    @staticmethod
    def create(db: Session, data: CategoryCreate):
        payload = data.model_dump()
        existing = CategoryService._find_by_normalized_name(db, payload["name"])
        if existing:
            raise HTTPException(
                status_code=409,
                detail="Category with this name already exists",
            )

        category = Category(**payload)
        return CategoryRepository.create(db, category)

    @staticmethod
    def list(db: Session):
        return CategoryRepository.get_all(db)

    @staticmethod
    def update(db: Session, category_id: int, data: CategoryUpdate):
        category = CategoryRepository.get_by_id(db, category_id)
        if not category:
            return None

        payload = data.model_dump(exclude_unset=True)
        if "name" in payload:
            existing = CategoryService._find_by_normalized_name(db, payload["name"])
            if existing and existing.id != category_id:
                raise HTTPException(
                    status_code=409,
                    detail="Category with this name already exists",
                )

        for key, value in payload.items():
            setattr(category, key, value)

        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def delete(db: Session, category_id: int):
        category = CategoryRepository.get_by_id(db, category_id)
        if not category:
            return False

        CategoryRepository.delete(db, category)
        return True
