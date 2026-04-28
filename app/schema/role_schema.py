from pydantic import BaseModel
from typing import Optional


class RoleBase(BaseModel):
    name: str


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = None


class RoleResponse(RoleBase):
    id: int

    model_config = {
    "from_attributes": True
}

