from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints


ProductName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=180),
]
ProductDescription = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=4000),
]
TelegramFileId = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=1024),
]


class ProductCreate(BaseModel):
    name: ProductName
    description: ProductDescription | None = None
    subcategory_id: int
    image_file_id: TelegramFileId | None = None


class ProductUpdate(BaseModel):
    name: ProductName | None = None
    description: ProductDescription | None = None
    image_file_id: TelegramFileId | None = None


class ProductOut(BaseModel):
    id: int
    name: str
    description: str | None
    image_file_id: str | None
    subcategory_id: int

    model_config = ConfigDict(from_attributes=True)
