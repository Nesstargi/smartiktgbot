from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Product, Category, SubCategory, Lead

router = APIRouter()


# -------------------------
# КАТЕГОРИИ
# -------------------------
@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    return [{"id": c.id, "name": c.name} for c in db.query(Category).all()]


# -------------------------
# ПОДКАТЕГОРИИ
# -------------------------
@router.get("/subcategories/{cat_id}")
def get_subcategories(cat_id: int, db: Session = Depends(get_db)):
    return [
        {"id": s.id, "name": s.name}
        for s in db.query(SubCategory).filter(SubCategory.category_id == cat_id).all()
    ]


# -------------------------
# ТОВАРЫ
# -------------------------
@router.get("/products/{sub_id}")
def get_products(sub_id: int, db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.subcategory_id == sub_id).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "subcategory_id": p.subcategory_id,
            "image_file_id": p.image_file_id,  # ✅
        }
        for p in products
    ]


# -------------------------
# СОЗДАНИЕ ЗАЯВКИ
# -------------------------
@router.post("/leads")
def create_lead(data: dict, db: Session = Depends(get_db)):
    lead = Lead(
        name=data.get("name"),
        phone=data.get("phone"),
        telegram_id=data.get("telegram_id"),
        product=str(data.get("product")),
    )

    db.add(lead)
    db.commit()
    db.refresh(lead)

    return {"status": "ok"}
