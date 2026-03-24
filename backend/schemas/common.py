from typing import Literal

from pydantic import BaseModel


class OkStatusOut(BaseModel):
    status: Literal["ok"]


class StatusOut(BaseModel):
    status: Literal["deleted"]


class PermissionsOut(BaseModel):
    permissions: list[str]
