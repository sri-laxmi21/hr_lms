from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

# -------------------------------
# BASE SCHEMA
# -------------------------------

class MenuBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    display_name: str
    route: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[int] = None
    menu_order: Optional[int] = 0
    is_active: Optional[bool] = True
    module_id: int


# -------------------------------
# CREATE SCHEMA
# -------------------------------

class MenuCreate(MenuBase):
    """Used while creating menu"""
    pass


# -------------------------------
# UPDATE SCHEMA
# -------------------------------

class MenuUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = None
    display_name: Optional[str] = None
    route: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[int] = None
    menu_order: Optional[int] = None
    is_active: Optional[bool] = None
    module_id: Optional[int] = None


# -------------------------------
# RESPONSE SCHEMA
# -------------------------------

class MenuResponse(MenuBase):
    id: int

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    modified_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# -------------------------------
# TREE RESPONSE (NESTED MENUS)
# -------------------------------

class MenuTreeResponse(MenuResponse):
    children: List["MenuTreeResponse"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# -------------------------------
# FIX FOR FORWARD REFERENCES
# -------------------------------

MenuTreeResponse.model_rebuild()
