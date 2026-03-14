from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Category, SubCategory
from backend.schemas.subcategory import SubCategoryOut

router = APIRouter()


@router.get("/subcategories/{cat_id}", response_model=list[SubCategoryOut])
def get_subcategories(cat_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == cat_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return (
        db.query(SubCategory)
        .filter(SubCategory.category_id == cat_id)
        .order_by(SubCategory.id.asc())
        .all()
    )
