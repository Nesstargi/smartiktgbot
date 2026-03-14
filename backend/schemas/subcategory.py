from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints


SubCategoryName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=120),
]
ImageUrl = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=2048),
]


class SubCategoryCreate(BaseModel):
    name: SubCategoryName
    category_id: int
    image_url: ImageUrl | None = None


class SubCategoryUpdate(BaseModel):
    name: SubCategoryName | None = None
    image_url: ImageUrl | None = None


class SubCategoryOut(BaseModel):
    id: int
    name: str
    category_id: int
    image_url: str | None = None

    model_config = ConfigDict(from_attributes=True)
