from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from backend.config import BOT_API_TOKEN
from backend.database import get_db
from backend.schemas.bot_subscriber import BotSubscriberRegisterIn
from backend.schemas.common import OkStatusOut
from backend.services.bot_subscriber_service import BotSubscriberService

router = APIRouter()


@router.post("/bot-subscribers/register", response_model=OkStatusOut)
def register_bot_subscriber(
    data: BotSubscriberRegisterIn,
    db: Session = Depends(get_db),
    x_bot_token: str | None = Header(default=None),
):
    if BOT_API_TOKEN and x_bot_token != BOT_API_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    BotSubscriberService.register(db, data)
    return {"status": "ok"}
