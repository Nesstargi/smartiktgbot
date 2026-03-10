from pydantic import BaseModel, ConfigDict
from typing import Optional


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    subcategory_id: int
    image_file_id: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_file_id: Optional[str] = None


class ProductOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    image_file_id: Optional[str]
    subcategory_id: int

    model_config = ConfigDict(from_attributes=True)
