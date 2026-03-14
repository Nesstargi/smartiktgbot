from typing import Literal

from pydantic import BaseModel


class StatusOut(BaseModel):
    status: Literal["deleted"]


class PermissionsOut(BaseModel):
    permissions: list[str]
