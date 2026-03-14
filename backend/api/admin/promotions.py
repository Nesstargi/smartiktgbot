from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.deps import PERMISSION_MANAGE_PROMOTIONS, require_permission
from backend.database import get_db
from backend.models.lead import Lead
from backend.models.promotion import Promotion
from backend.schemas.promotion import PromotionCreate, PromotionOut, PromotionUpdate
from backend.services.notification_service import NotificationService

router = APIRouter()


@router.get("/", response_model=list[PromotionOut])
def list_promotions(
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_PROMOTIONS)),
):
    return db.query(Promotion).order_by(Promotion.id.desc()).all()


@router.post("/", response_model=PromotionOut)
async def create_promotion(
    data: PromotionCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_PROMOTIONS)),
):
    payload = data.model_dump()
    send_to_all = bool(payload.pop("send_to_all", False))

    item = Promotion(**payload)
    db.add(item)
    db.commit()
    db.refresh(item)

    if send_to_all:
        rows = (
            db.query(Lead.telegram_id)
            .filter(Lead.telegram_id.isnot(None))
            .distinct()
            .all()
        )
        chat_ids = [row[0] for row in rows if row[0]]
        await NotificationService.send_broadcast(
            chat_ids=chat_ids,
            title=f"Новая акция: {item.title}",
            message=item.description or "Смотрите подробности в боте.",
            image_url=item.image_url,
            image_file_id=item.image_file_id,
        )

    return item


@router.put("/{promotion_id}", response_model=PromotionOut)
def update_promotion(
    promotion_id: int,
    data: PromotionUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_PROMOTIONS)),
):
    item = db.query(Promotion).filter(Promotion.id == promotion_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Promotion not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{promotion_id}")
def delete_promotion(
    promotion_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_PROMOTIONS)),
):
    item = db.query(Promotion).filter(Promotion.id == promotion_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Promotion not found")

    db.delete(item)
    db.commit()
    return {"status": "deleted"}
