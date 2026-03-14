from pydantic import BaseModel, ConfigDict


class PromotionBase(BaseModel):
    title: str
    description: str | None = None
    image_url: str | None = None
    image_file_id: str | None = None
    is_active: bool = True


class PromotionCreate(PromotionBase):
    send_to_all: bool = False


class PromotionUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    image_url: str | None = None
    image_file_id: str | None = None
    is_active: bool | None = None


class PromotionOut(PromotionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class PromotionFileIdUpdate(BaseModel):
    image_file_id: str
