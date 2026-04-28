from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class RoleRightBase(BaseModel):
    role_id: int
    menu_id: int
    can_view: Optional[bool] = False
    can_create: Optional[bool] = False
    can_edit: Optional[bool] = False
    can_delete: Optional[bool] = False

class RoleRightCreate(RoleRightBase):
    pass

class RoleRightUpdate(BaseModel):
    can_view: Optional[bool] = None
    can_create: Optional[bool] = None
    can_edit: Optional[bool] = None
    can_delete: Optional[bool] = None

class RoleRightResponse(RoleRightBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    modified_by: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class RoleRightWithMenuResponse(BaseModel):
    id: int
    menu_id: int
    menu_name: str
    menu_display_name: str
    menu_route: Optional[str] = None
    can_view: bool
    can_create: bool
    can_edit: bool
    can_delete: bool
    
    model_config = {
    "from_attributes": True
}


class BulkRoleRightCreate(BaseModel):
    role_id: int
    menu_id: int
    can_view: bool = False
    can_create: bool = False
    can_edit: bool = False
    can_delete: bool = False

class BulkRoleRightRequest(BaseModel):
    role_id: int
    rights: list[BulkRoleRightCreate]