from pydantic import BaseModel, Field


class BroadcastNotificationIn(BaseModel):
    title: str = Field(min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=4096)
    image_url: str | None = None
