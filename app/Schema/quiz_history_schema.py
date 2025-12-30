from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class QuizHistoryBase(BaseModel):
    user_id: int
    checkpoint_id: int
    course_id: int
    video_id: int  # ✅ add video_id
    answer: Optional[str] = None
    result: Optional[str] = None
    question: Optional[str] = None

class QuizHistoryCreate(QuizHistoryBase):
    pass

# Response with message
class QuizHistoryMessageResponse(BaseModel):
    message: str 
    id: int
    user_id: int
    checkpoint_id: int
    course_id: int
    video_id: int  # ✅ add video_id
    answer: Optional[str] = None
    result: Optional[str] = None
    question: Optional[str] = None
    completed_at: datetime

    

class QuizHistoryResponse(QuizHistoryBase):
    id: int
    completed_at: datetime

    model_config = {
    "from_attributes": True
}

