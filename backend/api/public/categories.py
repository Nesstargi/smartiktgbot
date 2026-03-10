from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Category

router = APIRouter()


@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    return [{"id": c.id, "name": c.name} for c in db.query(Category).all()]
