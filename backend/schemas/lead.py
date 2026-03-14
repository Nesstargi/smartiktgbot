from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator


LeadName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=255),
]
LeadPhone = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=5, max_length=32),
]


class LeadCreate(BaseModel):
    name: LeadName | None = None
    phone: LeadPhone
    telegram_id: str | int | None = None
    product: str | int | None = None

    @field_validator("telegram_id", "product", mode="before")
    @classmethod
    def strip_optional_values(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class LeadOut(BaseModel):
    id: int
    name: str | None = None
    phone: str
    telegram_id: str | None = None
    product: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
