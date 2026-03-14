from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.category import Category
from backend.models.subcategory import SubCategory
from backend.repositories.subcategory_repo import SubCategoryRepository
from backend.schemas.subcategory import SubCategoryCreate, SubCategoryUpdate


class SubCategoryService:
    @staticmethod
    def _get_category_or_404(db: Session, category_id: int):
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category

    @staticmethod
    def _find_duplicate(db: Session, *, category_id: int, name: str):
        return (
            db.query(SubCategory)
            .filter(
                SubCategory.category_id == category_id,
                func.lower(SubCategory.name) == name.lower(),
            )
            .first()
        )

    @staticmethod
    def create(db: Session, data: SubCategoryCreate):
        payload = data.model_dump()
        SubCategoryService._get_category_or_404(db, payload["category_id"])
        existing = SubCategoryService._find_duplicate(
            db,
            category_id=payload["category_id"],
            name=payload["name"],
        )
        if existing:
            raise HTTPException(
                status_code=409,
                detail="Subcategory with this name already exists in this category",
            )

        subcategory = SubCategory(**payload)
        return SubCategoryRepository.create(db, subcategory)

    @staticmethod
    def list(db: Session):
        return SubCategoryRepository.get_all(db)

    @staticmethod
    def update(db: Session, subcategory_id: int, data: SubCategoryUpdate):
        subcategory = SubCategoryRepository.get_by_id(db, subcategory_id)
        if not subcategory:
            return None

        payload = data.model_dump(exclude_unset=True)
        if "name" in payload:
            existing = SubCategoryService._find_duplicate(
                db,
                category_id=subcategory.category_id,
                name=payload["name"],
            )
            if existing and existing.id != subcategory_id:
                raise HTTPException(
                    status_code=409,
                    detail="Subcategory with this name already exists in this category",
                )

        for key, value in payload.items():
            setattr(subcategory, key, value)

        db.commit()
        db.refresh(subcategory)
        return subcategory

    @staticmethod
    def delete(db: Session, subcategory_id: int):
        subcategory = SubCategoryRepository.get_by_id(db, subcategory_id)
        if not subcategory:
            return False

        SubCategoryRepository.delete(db, subcategory)
        return True
