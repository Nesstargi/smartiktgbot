from sqlalchemy.orm import Session
from backend.models.category import Category
from backend.repositories.category_repo import CategoryRepository
from backend.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:

    @staticmethod
    def create(db: Session, data: CategoryCreate):
        category = Category(**data.dict())
        return CategoryRepository.create(db, category)

    @staticmethod
    def list(db: Session):
        return CategoryRepository.get_all(db)

    @staticmethod
    def update(db: Session, category_id: int, data: CategoryUpdate):
        category = CategoryRepository.get_by_id(db, category_id)
        if not category:
            return None

        for key, value in data.dict(exclude_unset=True).items():
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
