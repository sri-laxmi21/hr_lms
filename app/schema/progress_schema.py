from pydantic import BaseModel
from datetime import datetime

# Used for updating progress after video/quiz checkpoint
class ProgressUpdateSchema(BaseModel):
    user_id: int
    course_id: int
    watched_minutes: float  # frontend sends current watched minutes


# Response schema
class ProgressResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    watched_minutes: float
    progress_percentage: float
    created_at: datetime
    updated_at: datetime

    model_config = {
    "from_attributes": True
}
  # ✅ Use this for Pydantic v1
