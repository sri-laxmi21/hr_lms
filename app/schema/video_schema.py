from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime
from app.schema.quiz_checkpoint_schema import QuizCheckpointResponse  # Import checkpoints

class VideoBase(BaseModel):
    title: Optional[str]
    youtube_url: str
    duration: Optional[float] = 0.0

class VideoCreate(VideoBase):
    course_id: int

class VideoUpdate(BaseModel):
    title: Optional[str]
    youtube_url: Optional[HttpUrl] = None
    duration: Optional[float] = 0.0

class VideoResponse(VideoBase):
    id: int
    course_id: int
    checkpoints: List[QuizCheckpointResponse] = []  # Bind checkpoints
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
    "from_attributes": True
}
 # ✅ must have for .from_orm()
