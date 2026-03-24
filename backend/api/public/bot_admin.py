from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from backend.config import BOT_API_TOKEN
from backend.database import get_db
from backend.models import BotSubscriber, Lead
from backend.schemas.bot_admin import BotAdminOverviewOut

router = APIRouter()


@router.get("/bot-admin/overview", response_model=BotAdminOverviewOut)
def get_bot_admin_overview(
    limit: int = Query(default=10, ge=1, le=20),
    db: Session = Depends(get_db),
    x_bot_token: str | None = Header(default=None),
):
    if BOT_API_TOKEN and x_bot_token != BOT_API_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    recent_leads = (
        db.query(Lead)
        .order_by(Lead.created_at.desc(), Lead.id.desc())
        .limit(limit)
        .all()
    )

    return {
        "bot_users": db.query(BotSubscriber).count(),
        "leads_total": db.query(Lead).count(),
        "recent_leads": recent_leads,
    }
