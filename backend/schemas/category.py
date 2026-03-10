from pydantic import BaseModel, ConfigDict
from typing import Optional


class CategoryCreate(BaseModel):
    name: str


class CategoryUpdate(BaseModel):
    name: Optional[str] = None


class CategoryOut(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)
