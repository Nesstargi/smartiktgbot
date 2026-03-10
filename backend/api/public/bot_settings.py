from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.bot_setting import BotSetting
from backend.schemas.bot_setting import (
    BotSettingsOut,
    DEFAULT_ABOUT_MESSAGE,
    DEFAULT_CONSULTATION_CONTACT_PROMPT,
    DEFAULT_CONSULTATION_MESSAGE,
    DEFAULT_CONSULTATION_PHONE,
    DEFAULT_REMINDER,
)

router = APIRouter()


DEFAULT_REMINDER_DELAY = 30


@router.get("/bot-settings", response_model=BotSettingsOut)
def get_bot_settings(db: Session = Depends(get_db)):
    settings = db.query(BotSetting).filter(BotSetting.id == 1).first()
    if not settings:
        settings = BotSetting(id=1)
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return {
        "start_message": settings.start_message,
        "abandoned_reminder_message": settings.abandoned_reminder_message
        or DEFAULT_REMINDER,
        "abandoned_reminder_delay_minutes": settings.abandoned_reminder_delay_minutes
        or DEFAULT_REMINDER_DELAY,
        "consultation_phone": settings.consultation_phone or DEFAULT_CONSULTATION_PHONE,
        "consultation_message": settings.consultation_message or DEFAULT_CONSULTATION_MESSAGE,
        "consultation_contact_prompt": settings.consultation_contact_prompt
        or DEFAULT_CONSULTATION_CONTACT_PROMPT,
        "about_message": settings.about_message or DEFAULT_ABOUT_MESSAGE,
    }
