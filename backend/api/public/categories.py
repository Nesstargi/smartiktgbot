from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Category
from backend.schemas.category import CategoryOut

router = APIRouter()


@router.get("/categories", response_model=list[CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.id.asc()).all()
