from pydantic import BaseModel
from typing import Optional

# For reading from DB
class ModuleBase(BaseModel):
    name: str
    display_name: str

class ModuleCreate(ModuleBase):
    pass  # used when creating new module

class ModuleUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None

class ModuleOut(ModuleBase):
    id: int

    class Config:
        from_attributes = True  # important for SQLAlchemy model support

from app.schema.menu_schema import MenuTreeResponse
from typing import List

class ModuleWithMenus(ModuleOut):
    menus: List[MenuTreeResponse] = []

