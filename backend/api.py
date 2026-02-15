from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend import models

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close


@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()


@router.get("/subcategories/{cat_id}")
def get_subcategories(cat_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.SubCategory)
        .filter(models.SubCategory.category_id == cat_id)
        .all()
    )


@router.get("/products/{sub_id}")
def get_products(sub_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Product).filter(models.Product.subcategory_id == sub_id).all()
    )
