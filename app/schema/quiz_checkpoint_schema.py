from pydantic import BaseModel, Field
from typing import Optional

# Schema for creating a checkpoint
class QuizCheckpointCreate(BaseModel):
    course_id: int  # ✅ course link
    video_id: int
    timestamp: float
    question: str
    choices: str
    correct_answer: str
    required: Optional[bool] = True

# Schema for updating a checkpoint
class QuizCheckpointUpdate(BaseModel):
    course_id: Optional[int]
    video_id: Optional[int]
    timestamp: Optional[float]
    question: Optional[str]
    choices: Optional[str]
    correct_answer: Optional[str]
    required: Optional[bool]

# Schema for returning a checkpoint
class QuizCheckpointResponse(BaseModel):
    id: int
    course_id: int  # ✅ course
    video_id: int
    timestamp: float
    question: str
    choices: str
    correct_answer: str
    required: bool

    model_config = {
    "from_attributes": True
}
  # ✅ Fix for from_orm
