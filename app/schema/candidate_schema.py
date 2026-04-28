from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional, List
from datetime import date, datetime


# ============================================================
# BASE SCHEMA (Common fields)
# ============================================================
class CandidateBase(BaseModel):
    job_posting_id: Optional[int]

    # Basic info
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    applied_date: Optional[date]
    resume_url: Optional[str]
    status: Optional[str] = "Pending"

    # Candidate type
    candidate_type: str  # fresher / experienced

    # Education / skills
    highest_qualification: Optional[str]
    skills: Optional[str]

    # Fresher fields
    college_name: Optional[str]
    graduation_year: Optional[int]
    course: Optional[str]
    cgpa: Optional[str]

    # Experienced fields
    total_experience: Optional[str]
    previous_company: Optional[str]
    last_ctc: Optional[int]

    # Language levels
    telugu_level: Optional[str]
    english_level: Optional[str]
    hindi_level: Optional[str]

    # Personal
    gender: Optional[str]
    date_of_birth: Optional[date]

    # Address
    address_line1: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    pincode: Optional[str]


# ============================================================
# CREATE SCHEMA (Used internally if needed)
# ============================================================
class CandidateCreate(CandidateBase):
    pass


# ============================================================
# UPDATE SCHEMA
# ============================================================
class CandidateUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[EmailStr]
    phone_number: Optional[str]

    highest_qualification: Optional[str]
    skills: Optional[str]

    college_name: Optional[str]
    graduation_year: Optional[int]
    course: Optional[str]
    cgpa: Optional[str]

    total_experience: Optional[str]
    previous_company: Optional[str]
    last_ctc: Optional[int]

    telugu_level: Optional[str]
    english_level: Optional[str]
    hindi_level: Optional[str]

    gender: Optional[str]
    date_of_birth: Optional[date]

    address_line1: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    pincode: Optional[str]

    status: Optional[str]


# ============================================================
# RESPONSE SCHEMA (What API returns)
# ============================================================
class CandidateResponse(CandidateBase):
    id: int

    # Metadata
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[str]
    modified_by: Optional[str]

    model_config = ConfigDict(from_attributes=True)
