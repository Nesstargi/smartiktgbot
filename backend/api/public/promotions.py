from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from backend.config import BOT_API_TOKEN
from backend.database import get_db
from backend.models.promotion import Promotion
from backend.schemas.promotion import PromotionFileIdUpdate, PromotionOut

router = APIRouter()


@router.get("/promotions", response_model=list[PromotionOut])
def get_promotions(db: Session = Depends(get_db)):
    return (
        db.query(Promotion)
        .filter(Promotion.is_active.is_(True))
        .order_by(Promotion.id.desc())
        .all()
    )


@router.post("/promotions/{promotion_id}/file-id", response_model=PromotionOut)
def set_promotion_file_id(
    promotion_id: int,
    data: PromotionFileIdUpdate,
    db: Session = Depends(get_db),
    x_bot_token: str | None = Header(default=None),
):
    if BOT_API_TOKEN and x_bot_token != BOT_API_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    item = db.query(Promotion).filter(Promotion.id == promotion_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Promotion not found")

    if item.image_file_id != data.image_file_id:
        item.image_file_id = data.image_file_id
        db.commit()
        db.refresh(item)

    return item
