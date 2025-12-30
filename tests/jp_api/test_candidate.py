import pytest
from datetime import datetime
from app.models.candidate_m import Candidate
from app.models.job_posting_m import JobType

# ==========================================
# Candidate Tests
# ==========================================

def test_apply_fresher_candidate(db_session, user, create_candidate):
    candidate = create_candidate(
        candidate_type="fresher",  # matches your Candidate model string
        college_name="ABC College",
        graduation_year=2024,
        course="B.Tech",
        cgpa="8.5",
        job_type=JobType.fresher
    )

    assert candidate.candidate_type == "fresher"
    assert candidate.college_name == "ABC College"
    assert candidate.job_posting.job_type == JobType.fresher
    assert candidate.status == "Pending"


def test_apply_experienced_candidate(db_session, user, create_candidate):
    candidate = create_candidate(
        candidate_type="experienced",
        total_experience="3 years",
        previous_company="XYZ Ltd",
        last_ctc=600000,
        job_type=JobType.experienced
    )

    assert candidate.candidate_type == "experienced"
    assert candidate.total_experience == "3 years"
    assert candidate.previous_company == "XYZ Ltd"
    assert candidate.job_posting.job_type == JobType.experienced
    assert candidate.status == "Pending"


def test_apply_candidate_missing_fields(db_session, user, create_candidate):
    # Fresher with minimal fields
    candidate = create_candidate(candidate_type="fresher", job_type=JobType.fresher)
    assert candidate.candidate_type == "fresher"
    assert candidate.job_posting.job_type == JobType.fresher
    assert candidate.status == "Pending"

    # Experienced with minimal fields
    candidate2 = create_candidate(candidate_type="experienced", job_type=JobType.experienced)
    assert candidate2.candidate_type == "experienced"
    assert candidate2.job_posting.job_type == JobType.experienced
    assert candidate2.status == "Pending"


def test_get_all_candidates_with_data(db_session, user, create_candidate):
    # Create multiple candidates
    candidate1 = create_candidate(candidate_type="fresher", job_type=JobType.fresher)
    candidate2 = create_candidate(candidate_type="experienced", job_type=JobType.experienced)

    all_candidates = db_session.query(Candidate).all()
    assert len(all_candidates) >= 2
    assert all_candidates[0].job_posting is not None
    assert all_candidates[1].job_posting is not None
