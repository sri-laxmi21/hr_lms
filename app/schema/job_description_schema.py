from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class JobDescriptionBase(BaseModel):
    title: str
    description: Optional[str] = None
    required_skills: Optional[str] = None

class JobDescriptionCreate(JobDescriptionBase):
    pass

class JobDescriptionUpdate(JobDescriptionBase):
    pass

class JobDescriptionResponse(JobDescriptionBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True  # Pydantic v2
    }
