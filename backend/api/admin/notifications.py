from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.deps import PERMISSION_MANAGE_NOTIFICATIONS, require_permission
from backend.database import get_db
from backend.schemas.notification import BroadcastNotificationIn, BroadcastNotificationOut
from backend.services.bot_subscriber_service import BotSubscriberService
from backend.services.notification_service import NotificationService

router = APIRouter()


@router.post("/broadcast", response_model=BroadcastNotificationOut)
async def broadcast_notification(
    data: BroadcastNotificationIn,
    db: Session = Depends(get_db),
    admin=Depends(require_permission(PERMISSION_MANAGE_NOTIFICATIONS)),
):
    result = await NotificationService.send_broadcast(
        chat_ids=BotSubscriberService.broadcast_chat_ids(db),
        title=data.title,
        message=data.message,
        image_url=data.image_url,
    )
    return result
