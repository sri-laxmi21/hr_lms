# app/schema/course_schema.py
from pydantic import BaseModel
from typing import List, Optional
from app.schema.video_schema import VideoResponse


class CourseBase(BaseModel):
    title: str
    instructor: str
    level: Optional[str] = "beginner"
    price: Optional[float] = 0.0
    category_id: Optional[int] = None


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    instructor: Optional[str] = None
    level: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None


class CourseResponse(CourseBase):
    id: int
    videos: List[VideoResponse] = []
    duration: Optional[float] = 0.0

    model_config = {
    "from_attributes": True
}
  # allows from_orm() conversion
