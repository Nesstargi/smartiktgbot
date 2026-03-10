from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Product

router = APIRouter()


@router.get("/products/{sub_id}")
def get_products(sub_id: int, db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.subcategory_id == sub_id).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "subcategory_id": p.subcategory_id,
            "image_file_id": p.image_file_id,
        }
        for p in products
    ]
