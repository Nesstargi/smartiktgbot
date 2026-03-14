from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.deps import PERMISSION_MANAGE_NOTIFICATIONS, require_permission
from backend.database import get_db
from backend.models.lead import Lead
from backend.schemas.notification import BroadcastNotificationIn, BroadcastNotificationOut
from backend.services.notification_service import NotificationService

router = APIRouter()


@router.post("/broadcast", response_model=BroadcastNotificationOut)
async def broadcast_notification(
    data: BroadcastNotificationIn,
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_NOTIFICATIONS)),
):
    rows = (
        db.query(Lead.telegram_id)
        .filter(Lead.telegram_id.isnot(None))
        .distinct()
        .all()
    )
    chat_ids = [row[0] for row in rows if row[0]]

    result = await NotificationService.send_broadcast(
        chat_ids=chat_ids,
        title=data.title,
        message=data.message,
        image_url=data.image_url,
    )
    return result
