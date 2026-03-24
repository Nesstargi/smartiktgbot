from pydantic import BaseModel, Field, field_validator


class BotSubscriberRegisterIn(BaseModel):
    chat_id: str | int
    telegram_user_id: str | int | None = None
    username: str | None = Field(default=None, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)

    @field_validator("chat_id", "telegram_user_id", "username", "full_name", mode="before")
    @classmethod
    def normalize_optional_values(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return str(value)

    @field_validator("chat_id")
    @classmethod
    def validate_chat_id(cls, value):
        if value is None:
            raise ValueError("chat_id is required")
        value = str(value).strip()
        if not value:
            raise ValueError("chat_id is required")
        return value
