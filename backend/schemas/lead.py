from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LeadCreate(BaseModel):
    name: str | None = None
    phone: str = Field(min_length=5, max_length=32)
    telegram_id: str | int | None = None
    product: str | int | None = None


class LeadOut(BaseModel):
    id: int
    name: str | None = None
    phone: str
    telegram_id: str | None = None
    product: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
