from pydantic import BaseModel, Field


class AdminUserCreate(BaseModel):
    email: str
    password: str = Field(min_length=8)
    is_super_admin: bool = False
    permissions: list[str] = Field(default_factory=list)


class AdminUserPermissionsUpdate(BaseModel):
    permissions: list[str]


class AdminUserRoleUpdate(BaseModel):
    is_super_admin: bool


class AdminUserOut(BaseModel):
    id: int
    email: str
    is_active: bool
    roles: list[str]
    permissions: list[str]


