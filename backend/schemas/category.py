from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints


CategoryName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=120),
]


class CategoryCreate(BaseModel):
    name: CategoryName


class CategoryUpdate(BaseModel):
    name: CategoryName | None = None


class CategoryOut(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)
