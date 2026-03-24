from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BotAdminRecentLeadOut(BaseModel):
    id: int
    name: str | None = None
    phone: str
    telegram_id: str | None = None
    product: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class BotAdminOverviewOut(BaseModel):
    bot_users: int = Field(ge=0)
    leads_total: int = Field(ge=0)
    recent_leads: list[BotAdminRecentLeadOut]
