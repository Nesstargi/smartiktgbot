from pydantic import BaseModel, Field


class DashboardStatsOut(BaseModel):
    products: int = Field(ge=0)
    categories: int = Field(ge=0)
    subcategories: int = Field(ge=0)
    promotions: int = Field(ge=0)
    leads: int = Field(ge=0)
