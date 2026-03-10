from sqlalchemy.orm import Session
from backend.models.subcategory import SubCategory


class SubCategoryRepository:

    @staticmethod
    def create(db: Session, subcategory: SubCategory):
        db.add(subcategory)
        db.commit()
        db.refresh(subcategory)
        return subcategory

    @staticmethod
    def get_all(db: Session):
        return db.query(SubCategory).all()

    @staticmethod
    def get_by_id(db: Session, subcategory_id: int):
        return db.query(SubCategory).filter(SubCategory.id == subcategory_id).first()

    @staticmethod
    def delete(db: Session, subcategory: SubCategory):
        db.delete(subcategory)
        db.commit()
