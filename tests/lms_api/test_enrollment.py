import pytest
from app.models.enrollment_m import Enrollment

# ==================================================
# CREATE ENROLLMENT
# ==================================================
def test_enroll_user_success(client, user, course, db_session):
    payload = {
        "user_id": user.id,
        "course_id": course.id
    }

    response = client.post("/enrollments/", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["user_id"] == user.id
    assert data["course_id"] == course.id

    enrollment = db_session.query(Enrollment).filter_by(
        user_id=user.id,
        course_id=course.id
    ).first()
    assert enrollment is not None


def test_enroll_user_not_found(client, course):
    payload = {
        "user_id": 99999,
        "course_id": course.id
    }

    response = client.post("/enrollments/", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_enroll_course_not_found(client, user):
    payload = {
        "user_id": user.id,
        "course_id": 99999
    }

    response = client.post("/enrollments/", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"


def test_enroll_duplicate(client, user, course):
    payload = {
        "user_id": user.id,
        "course_id": course.id
    }

    response1 = client.post("/enrollments/", json=payload)
    assert response1.status_code == 201

    response2 = client.post("/enrollments/", json=payload)
    assert response2.status_code == 400
    assert response2.json()["detail"] == "User already enrolled in this course"


# ==================================================
# LIST ENROLLMENTS
# ==================================================
def test_list_enrollments(client, enrollment):
    response = client.get("/enrollments/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


# ==================================================
# GET ENROLLMENTS BY USER
# ==================================================
def test_get_enrollments_by_user(client, enrollment, user):
    response = client.get(f"/enrollments/user/{user.id}")
    assert response.status_code == 200

    data = response.json()
    assert len(data) >= 1
    assert data[0]["user_id"] == user.id


# ==================================================
# GET ENROLLMENTS BY COURSE
# ==================================================
def test_get_enrollments_by_course(client, enrollment, course):
    response = client.get(f"/enrollments/course/{course.id}")
    assert response.status_code == 200

    data = response.json()
    assert len(data) >= 1
    assert data[0]["course_id"] == course.id


# ==================================================
# DELETE ENROLLMENT
# ==================================================
def test_delete_enrollment_success(client, enrollment, db_session):
    response = client.delete(f"/enrollments/{enrollment.id}")
    assert response.status_code == 204

    deleted = db_session.query(Enrollment).filter_by(id=enrollment.id).first()
    assert deleted is None


def test_delete_enrollment_not_found(client):
    response = client.delete("/enrollments/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Enrollment not found"
