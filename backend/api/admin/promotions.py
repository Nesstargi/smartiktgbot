from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.api.utils import normalize_search_query, paginate_query
from backend.core.deps import PERMISSION_MANAGE_PROMOTIONS, require_permission
from backend.database import get_db
from backend.models.lead import Lead
from backend.models.promotion import Promotion
from backend.schemas.common import StatusOut
from backend.schemas.promotion import PromotionCreate, PromotionOut, PromotionUpdate
from backend.services.notification_service import NotificationService
from backend.services.promotion_service import PromotionService

router = APIRouter()


def _broadcast_chat_ids(db: Session) -> list[str]:
    rows = (
        db.query(Lead.telegram_id)
        .filter(Lead.telegram_id.isnot(None))
        .distinct()
        .all()
    )
    return [row[0] for row in rows if row[0]]


@router.get("/", response_model=list[PromotionOut])
def list_promotions(
    response: Response,
    q: str | None = Query(default=None, max_length=200),
    is_active: bool | None = Query(default=None),
    limit: int | None = Query(default=None, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_PROMOTIONS)),
):
    query = db.query(Promotion)
    term = normalize_search_query(q)
    if term:
        pattern = f"%{term}%"
        query = query.filter(
            or_(
                Promotion.title.ilike(pattern),
                Promotion.description.ilike(pattern),
            )
        )
    if is_active is not None:
        query = query.filter(Promotion.is_active.is_(is_active))

    return paginate_query(
        query.order_by(Promotion.id.desc()),
        response,
        limit=limit,
        offset=offset,
    )


@router.post("/", response_model=PromotionOut)
async def create_promotion(
    data: PromotionCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_PROMOTIONS)),
):
    if data.send_to_all and not NotificationService.is_configured():
        raise HTTPException(
            status_code=503,
            detail="Notification service is not configured",
        )

    item = PromotionService.create(db, data)

    if data.send_to_all:
        await NotificationService.send_broadcast(
            chat_ids=_broadcast_chat_ids(db),
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
    item = PromotionService.update(db, promotion_id, data)
    if not item:
        raise HTTPException(status_code=404, detail="Promotion not found")
    return item


@router.delete("/{promotion_id}", response_model=StatusOut)
def delete_promotion(
    promotion_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_PROMOTIONS)),
):
    ok = PromotionService.delete(db, promotion_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Promotion not found")
    return {"status": "deleted"}
