# tests/conftest.py
import uuid
import pytest
from app.main import app
from datetime import datetime
from app.config import settings
from app.models.organization_m import Organization
from app.models.branch_m import Branch
from app.models.job_description_m import JobDescription
from app.models.candidate_m import Candidate
from app.models.course_m import Course
from app.models.video_m import Video
from app.models.category_m import Category
from app.models.user_m import User
from app.models.enrollment_m import Enrollment
from app.models.Progress_m import Progress
from app.models.QuizHistory_m import QuizHistory
from app.models.QuizCheckpoint_m import QuizCheckpoint
from app.schema.candidate_schema import CandidateBase
from app.schema.job_posting_schema import JobType

from app.permission_dependencies import (
    require_view_permission,
    require_create_permission,
    require_edit_permission,
    require_delete_permission
)

# ======================================================
# PERMISSION OVERRIDES (FACTORY-SAFE)
# ======================================================
# ======================================================
# PERMISSION OVERRIDES (FINAL & CORRECT)
# ======================================================
@pytest.fixture(autouse=True)
def override_permissions():
    def allow_all_permission(*args, **kwargs):
        return True

    # IMPORTANT: override FACTORY, not returned dependency
    app.dependency_overrides[require_view_permission] = (
        lambda *args, **kwargs: allow_all_permission
    )
    app.dependency_overrides[require_create_permission] = (
        lambda *args, **kwargs: allow_all_permission
    )
    app.dependency_overrides[require_edit_permission] = (
        lambda *args, **kwargs: allow_all_permission
    )
    app.dependency_overrides[require_delete_permission] = (
        lambda *args, **kwargs: allow_all_permission
    )

    yield
    app.dependency_overrides.clear()


# ======================================================
# AWS MOCK SETTINGS
# ======================================================
settings.AWS_REGION = getattr(settings, "AWS_REGION_RESUME", "eu-north-1")
settings.AWS_BUCKET_NAME = getattr(settings, "BUCKET_NAME_RESUME", "test-bucket")
settings.AWS_ACCESS_KEY_ID = getattr(settings, "AWS_ACCESS_KEY_ID_RESUME", "test-access-key")
settings.AWS_SECRET_ACCESS_KEY = getattr(
    settings, "AWS_SECRET_ACCESS_KEY_RESUME", "test-secret-key"
)

# ======================================================
# ORGANIZATION
# ======================================================
@pytest.fixture
def organization(db_session):
    org = Organization(
        name=f"Test Org {uuid.uuid4()}",
        subscription_status="active",
        branch_limit=5,
        user_limit=10,
        storage_limit_mb=1000,
        current_storage_mb=0,
        current_branches=0,
        current_users=0,
        total_amount_paid=0,
        is_active=True
    )
    db_session.add(org)
    db_session.flush()
    return org

# ======================================================
# BRANCH
# ======================================================
@pytest.fixture
def branch(db_session, organization):
    branch = Branch(
        name=f"Bangalore Branch {uuid.uuid4()}",
        organization_id=organization.id
    )
    db_session.add(branch)
    db_session.flush()
    return branch

# ======================================================
# JOB DESCRIPTION
# ======================================================
@pytest.fixture
def job_description(db_session):
    jd = JobDescription(
        title=f"Python Developer {uuid.uuid4()}",
        description="FastAPI + SQLAlchemy",
        required_skills="Python, FastAPI"
    )
    db_session.add(jd)
    db_session.flush()
    return jd

# ======================================================
# CANDIDATE
# ======================================================
@pytest.fixture
def candidate(db_session):
    candidate = Candidate(
        first_name="John",
        last_name="Doe",
        email=f"john.{uuid.uuid4()}@test.com",
        phone_number="9876543210",
        candidate_type="Fresher"
    )
    db_session.add(candidate)
    db_session.flush()
    return candidate

# ======================================================
# S3 MOCK
# ======================================================
@pytest.fixture(autouse=True)
def mock_s3_upload(monkeypatch):
    def fake_upload(file, folder="candidate_docs"):
        return f"https://test-bucket.s3.amazonaws.com/{folder}/{file.filename}"

    monkeypatch.setattr(
        "app.s3_helper.upload_file_to_s3",
        fake_upload
    )

# ======================================================
# MOCK RESUME FILE  
# ======================================================
@pytest.fixture
def create_mock_resume():
    def _create():
        from io import BytesIO
        return ("resume.pdf", BytesIO(b"Mock PDF Resume Content"), "application/pdf")
    return _create

# ======================================================
# JOB POSTING (FIXED)
# ======================================================
@pytest.fixture
def create_job_posting(db_session, organization, branch, job_description):
    from app.models.job_posting_m import JobPosting

    def _create(
        job_type="Full Time",
        number_of_positions=1,
        employment_type="Full Time",
        location="Hyderabad",
        salary=50000
    ):
        job = JobPosting(
            organization_id=organization.id,
            branch_id=branch.id,
            job_description_id=job_description.id,
            job_type=job_type,
            number_of_positions=number_of_positions,
            employment_type=employment_type,
            location=location,
            salary=salary,
            posting_date=datetime.utcnow(),
            closing_date=datetime.utcnow(),
            approval_status="accepted"
        )
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)
        return job

    return _create


# ======================================================
# CATEGORY
# ======================================================
@pytest.fixture
def category(db_session):
    category = Category(name="Programming")
    db_session.add(category)
    db_session.flush()
    return category

# ======================================================
# COURSE
# ======================================================
@pytest.fixture
def course(db_session, organization, branch, category):
    course = Course(
        title=f"Python Course {uuid.uuid4()}",
        instructor="Test Instructor",
        level="beginner",
        duration=0.0,
        price=0.0,
        category_id=category.id,
        organization_id=organization.id,
        branch_id=branch.id
    )
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)
    return course

# ======================================================
# VIDEO
# ======================================================
@pytest.fixture
def video(db_session, course):
    video = Video(
        title="Intro Video",
        youtube_url="https://youtube.com/watch?v=fixture123",
        duration=10.0,
        course_id=course.id
    )
    db_session.add(video)
    db_session.flush()
    return video

# ======================================================
# USER
# ======================================================
@pytest.fixture
def user(db_session, organization, branch):
    user = User(
        first_name="Test",
        last_name="User",
        email=f"user_{uuid.uuid4()}@test.com",
        role_id=1,
        hashed_password="testhashedpassword123", 
        organization_id=organization.id,
        branch_id=branch.id
    )
    db_session.add(user)
    db_session.flush()
    return user

# ======================================================
# ENROLLMENT
# ======================================================
@pytest.fixture
def enrollment(db_session, user, course):
    enrollment = Enrollment(user_id=user.id, course_id=course.id)
    db_session.add(enrollment)
    db_session.commit()
    db_session.refresh(enrollment)
    return enrollment

# ======================================================
# PROGRESS
# ======================================================
@pytest.fixture
def progress(db_session, user, course):
    watched_minutes = 60.0
    dummy_progress = Progress(
        user_id=user.id,
        course_id=course.id,
        watched_minutes=watched_minutes,
        progress_percentage=min((watched_minutes / course.duration) * 100, 100.0),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(dummy_progress)
    db_session.commit()
    db_session.refresh(dummy_progress)
    return dummy_progress

# ======================================================
# QUIZ CHECKPOINT
# ======================================================
@pytest.fixture
def checkpoint(db_session, course, video):
    checkpoint = QuizCheckpoint(
        course_id=course.id,
        video_id=video.id,
        timestamp=10.0,
        question="What is FastAPI?",
        choices="Framework,Database,Language,Tool",
        correct_answer="Framework",
        required=True
    )
    db_session.add(checkpoint)
    db_session.commit()
    db_session.refresh(checkpoint)
    return checkpoint

# ======================================================
# QUIZ HISTORY
# ======================================================
@pytest.fixture
def quiz_history(db_session, user, checkpoint, video, course):
    history = QuizHistory(
        user_id=user.id,
        checkpoint_id=checkpoint.id,
        course_id=course.id,
        video_id=video.id,
        answer="Sample Answer",
        result=True,
        question="Sample Question?"
    )
    db_session.add(history)
    db_session.commit()
    db_session.refresh(history)
    return history

# ======================================================
# CREATE CANDIDATE FACTORY
# ======================================================
import pytest
from datetime import datetime
from app.models.candidate_m import Candidate
@pytest.fixture
def create_candidate(db_session, user, create_job_posting):
    def _create(
        candidate_type="fresher",
        total_experience=None,
        college_name=None,
        graduation_year=None,
        course=None,
        cgpa=None,
        previous_company=None,
        last_ctc=None,
        resume_url="http://resume.com/resume.pdf",
        job_type=None,
        first_name="John",
        last_name="Doe",
        email=None,
        phone_number="1234567890"
    ):
        # Convert Enum → string
        jt = job_type.value if hasattr(job_type, "value") else job_type

        # job_type ONLY goes to JobPosting
        job_posting = create_job_posting(job_type=jt)

        candidate = Candidate(
            job_posting_id=job_posting.id,
            first_name=first_name,
            last_name=last_name,
            email=email or f"user_{datetime.utcnow().timestamp()}@test.com",
            phone_number=phone_number,
            candidate_type=candidate_type,
            total_experience=total_experience,
            college_name=college_name,
            graduation_year=graduation_year,
            course=course,
            cgpa=cgpa,
            previous_company=previous_company,
            last_ctc=last_ctc,
            resume_url=resume_url,
            status="Pending",
            applied_date=datetime.utcnow()
        )

        db_session.add(candidate)
        db_session.commit()
        db_session.refresh(candidate)
        return candidate

    return _create
