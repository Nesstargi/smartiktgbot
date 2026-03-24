import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Lead
from backend.schemas.bot_subscriber import BotSubscriberRegisterIn
from backend.schemas.lead import LeadCreate
from backend.services.bot_subscriber_service import BotSubscriberService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/leads")
def create_lead(data: LeadCreate, db: Session = Depends(get_db)):
    lead = Lead(
        name=data.name,
        phone=data.phone,
        telegram_id=str(data.telegram_id) if data.telegram_id is not None else None,
        product=str(data.product) if data.product is not None else None,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)

    if data.telegram_id is not None:
        try:
            BotSubscriberService.register(
                db,
                BotSubscriberRegisterIn(
                    chat_id=data.telegram_id,
                    telegram_user_id=data.telegram_id,
                    full_name=data.name,
                ),
            )
        except Exception:
            db.rollback()
            logger.exception(
                "Lead subscriber sync failed for telegram_id=%s",
                data.telegram_id,
            )

    return {"status": "ok"}
