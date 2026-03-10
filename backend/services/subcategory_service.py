from sqlalchemy.orm import Session
from backend.models.subcategory import SubCategory
from backend.repositories.subcategory_repo import SubCategoryRepository
from backend.schemas.subcategory import SubCategoryCreate, SubCategoryUpdate


class SubCategoryService:

    @staticmethod
    def create(db: Session, data: SubCategoryCreate):
        subcategory = SubCategory(**data.dict())
        return SubCategoryRepository.create(db, subcategory)

    @staticmethod
    def list(db: Session):
        return SubCategoryRepository.get_all(db)

    @staticmethod
    def update(db: Session, subcategory_id: int, data: SubCategoryUpdate):
        subcategory = SubCategoryRepository.get_by_id(db, subcategory_id)
        if not subcategory:
            return None

        for key, value in data.dict(exclude_unset=True).items():
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
