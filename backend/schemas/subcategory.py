from pydantic import BaseModel, ConfigDict


class SubCategoryCreate(BaseModel):
    name: str
    category_id: int
    image_url: str | None = None


class SubCategoryUpdate(BaseModel):
    name: str | None = None
    image_url: str | None = None


class SubCategoryOut(BaseModel):
    id: int
    name: str
    category_id: int
    image_url: str | None = None

    model_config = ConfigDict(from_attributes=True)
