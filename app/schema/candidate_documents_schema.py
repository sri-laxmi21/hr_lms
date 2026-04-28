from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

# Base Schema
class CandidateDocumentBase(BaseModel):
    candidate_id: int
    document_type: str
    document_url: HttpUrl

# Create Schema
class CandidateDocumentCreate(CandidateDocumentBase):
    pass

# Update Schema
class CandidateDocumentUpdate(BaseModel):
    document_type: Optional[str] = None
    document_url: Optional[HttpUrl] = None

# Response Schema
class CandidateDocumentResponse(CandidateDocumentBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    modified_by: Optional[str] = None

    
    model_config = {
        "from_attributes": True  # was orm_mode in v1
    }
