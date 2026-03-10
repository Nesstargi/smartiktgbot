from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.deps import (
    PERMISSION_MANAGE_ABOUT,
    PERMISSION_MANAGE_BOT_SETTINGS,
    PERMISSION_MANAGE_CONSULTATION,
    require_any_permission,
)
from backend.database import get_db
from backend.models.bot_setting import BotSetting
from backend.schemas.bot_setting import (
    BotSettingsOut,
    BotSettingsUpdate,
    DEFAULT_ABOUT_MESSAGE,
    DEFAULT_CONSULTATION_CONTACT_PROMPT,
    DEFAULT_CONSULTATION_MESSAGE,
    DEFAULT_CONSULTATION_PHONE,
    DEFAULT_REMINDER,
)

router = APIRouter()


DEFAULT_REMINDER_DELAY = 30


def _get_or_create_settings(db: Session):
    settings = db.query(BotSetting).filter(BotSetting.id == 1).first()
    if settings:
        return settings

    settings = BotSetting(id=1)
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


def _settings_to_out(settings: BotSetting):
    return {
        "start_message": settings.start_message,
        "abandoned_reminder_message": settings.abandoned_reminder_message or DEFAULT_REMINDER,
        "abandoned_reminder_delay_minutes": settings.abandoned_reminder_delay_minutes
        or DEFAULT_REMINDER_DELAY,
        "consultation_phone": settings.consultation_phone or DEFAULT_CONSULTATION_PHONE,
        "consultation_message": settings.consultation_message or DEFAULT_CONSULTATION_MESSAGE,
        "consultation_contact_prompt": settings.consultation_contact_prompt
        or DEFAULT_CONSULTATION_CONTACT_PROMPT,
        "about_message": settings.about_message or DEFAULT_ABOUT_MESSAGE,
    }


@router.get("/", response_model=BotSettingsOut)
def get_settings(
    db: Session = Depends(get_db),
    admin=Depends(
        require_any_permission(
            [
                PERMISSION_MANAGE_BOT_SETTINGS,
                PERMISSION_MANAGE_CONSULTATION,
                PERMISSION_MANAGE_ABOUT,
            ]
        )
    ),
):
    settings = _get_or_create_settings(db)
    return _settings_to_out(settings)


@router.put("/", response_model=BotSettingsOut)
def update_settings(
    data: BotSettingsUpdate,
    db: Session = Depends(get_db),
    admin=Depends(
        require_any_permission(
            [
                PERMISSION_MANAGE_BOT_SETTINGS,
                PERMISSION_MANAGE_CONSULTATION,
                PERMISSION_MANAGE_ABOUT,
            ]
        )
    ),
):
    settings = _get_or_create_settings(db)
    settings.start_message = data.start_message
    settings.abandoned_reminder_message = data.abandoned_reminder_message
    settings.abandoned_reminder_delay_minutes = data.abandoned_reminder_delay_minutes
    settings.consultation_phone = data.consultation_phone
    settings.consultation_message = data.consultation_message
    settings.consultation_contact_prompt = data.consultation_contact_prompt
    settings.about_message = data.about_message
    db.commit()
    db.refresh(settings)
    return _settings_to_out(settings)
