from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.deps import require_role
from backend.database import get_db
from backend.models import Category, Lead, Product, Promotion, SubCategory
from backend.schemas.dashboard import DashboardStatsOut

router = APIRouter()


@router.get("/stats", response_model=DashboardStatsOut)
def get_stats(
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin")),
):
    return {
        "products": db.query(Product).count(),
        "categories": db.query(Category).count(),
        "subcategories": db.query(SubCategory).count(),
        "promotions": db.query(Promotion).count(),
        "leads": db.query(Lead).count(),
    }
