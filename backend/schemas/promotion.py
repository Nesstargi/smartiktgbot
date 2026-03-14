from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints


PromotionTitle = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=128),
]
PromotionDescription = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=4096),
]
PromotionImageUrl = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=2048),
]
PromotionImageFileId = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=1024),
]


class PromotionBase(BaseModel):
    title: PromotionTitle
    description: PromotionDescription | None = None
    image_url: PromotionImageUrl | None = None
    image_file_id: PromotionImageFileId | None = None
    is_active: bool = True


class PromotionCreate(PromotionBase):
    send_to_all: bool = False


class PromotionUpdate(BaseModel):
    title: PromotionTitle | None = None
    description: PromotionDescription | None = None
    image_url: PromotionImageUrl | None = None
    image_file_id: PromotionImageFileId | None = None
    is_active: bool | None = None


class PromotionOut(PromotionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class PromotionFileIdUpdate(BaseModel):
    image_file_id: PromotionImageFileId
