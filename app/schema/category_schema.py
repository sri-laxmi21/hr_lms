from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    courses: Optional[List["CourseResponse"]] = []

    model_config = ConfigDict(from_attributes=True)


# Import AFTER definition to solve circular import
from app.schema.course_schema import CourseResponse

# Pydantic v2 forward reference fix
CategoryResponse.model_rebuild()
