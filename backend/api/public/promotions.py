from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.promotion import Promotion
from backend.schemas.promotion import PromotionOut

router = APIRouter()


@router.get("/promotions", response_model=list[PromotionOut])
def get_promotions(db: Session = Depends(get_db)):
    return (
        db.query(Promotion)
        .filter(Promotion.is_active.is_(True))
        .order_by(Promotion.id.desc())
        .all()
    )
