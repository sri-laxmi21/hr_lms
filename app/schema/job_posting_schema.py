from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from enum import Enum


# ---------------------------
# ENUMS
# ---------------------------
class ApprovalStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class JobType(str, Enum):
    fresher = "fresher"
    experienced = "experienced"
    both = "both"


# ---------------------------
# BASE
# ---------------------------
class JobPostingBase(BaseModel):
    organization_id: int
    branch_id: int
    job_description_id: int
    job_type: JobType
    number_of_positions: int
    employment_type: str
    location: str
    salary: Optional[int] = None
    posting_date: date
    closing_date: Optional[date] = None


# ---------------------------
# CREATE
# ---------------------------
class JobPostingCreate(JobPostingBase):
    pass


# ---------------------------
# UPDATE
# ---------------------------
class JobPostingUpdate(BaseModel):
    branch_id: Optional[int] = None
    job_type: Optional[JobType] = None
    number_of_positions: Optional[int] = None
    employment_type: Optional[str] = None
    location: Optional[str] = None
    salary: Optional[int] = None
    posting_date: Optional[date] = None
    closing_date: Optional[date] = None
    approval_status: Optional[ApprovalStatus] = None


# ---------------------------
# RESPONSE
# ---------------------------
class JobPostingResponse(JobPostingBase):
    id: int
    approval_status: ApprovalStatus
    created_by: Optional[str]
    modified_by: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = {
        "from_attributes": True
    }
 # app/schema/job_dashboard_schema.py
from pydantic import BaseModel
from typing import List

class JobDashboardResponse(BaseModel):
    job_id: int
    job_type: str
    role: str
    location: str
    approval_status: str
    total_candidates: int
    pending: int
    accepted: int
    rejected: int
    