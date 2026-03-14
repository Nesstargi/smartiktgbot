from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Product, SubCategory
from backend.schemas.product import ProductOut

router = APIRouter()


@router.get("/products/{sub_id}", response_model=list[ProductOut])
def get_products(sub_id: int, db: Session = Depends(get_db)):
    subcategory = db.query(SubCategory).filter(SubCategory.id == sub_id).first()
    if not subcategory:
        raise HTTPException(status_code=404, detail="Subcategory not found")

    return (
        db.query(Product)
        .filter(Product.subcategory_id == sub_id)
        .order_by(Product.id.asc())
        .all()
    )
