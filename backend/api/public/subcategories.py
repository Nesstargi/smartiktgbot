from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import SubCategory

router = APIRouter()


@router.get("/subcategories/{cat_id}")
def get_subcategories(cat_id: int, db: Session = Depends(get_db)):
    return [
        {
            "id": s.id,
            "name": s.name,
            "category_id": s.category_id,
            "image_url": s.image_url,
        }
        for s in db.query(SubCategory).filter(SubCategory.category_id == cat_id).all()
    ]
