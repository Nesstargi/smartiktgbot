from sqlalchemy.orm import Session
from backend.models.category import Category


class CategoryRepository:

    @staticmethod
    def create(db: Session, category: Category):
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def get_all(db: Session):
        return db.query(Category).all()

    @staticmethod
    def get_by_id(db: Session, category_id: int):
        return db.query(Category).filter(Category.id == category_id).first()

    @staticmethod
    def delete(db: Session, category: Category):
        db.delete(category)
        db.commit()
