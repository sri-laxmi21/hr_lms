import pytest
from app.models.course_m import Course


# ==================================================
# CREATE COURSE
# ==================================================
def test_create_course_success(client, category, organization, branch, db_session):
    payload = {
        "title": "Python Basics",
        "instructor": "John Doe",
        "level": "beginner",
        "price": 0.0,
        "category_id": category.id,
        "organization_id": organization.id,
        "branch_id": branch.id
    }

    response = client.post("/courses/", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Python Basics"
    assert data["instructor"] == "John Doe"

    course = db_session.query(Course).filter_by(title="Python Basics").first()
    assert course is not None


def test_create_course_duplicate_title(client, category, organization, branch):
    payload = {
        "title": "Duplicate Course",
        "instructor": "Jane",
        "level": "intermediate",
        "price": 100.0,
        "category_id": category.id,
        "organization_id": organization.id,
        "branch_id": branch.id
    }

    # First create
    response1 = client.post("/courses/", json=payload)
    assert response1.status_code == 201

    # Duplicate create
    response2 = client.post("/courses/", json=payload)
    assert response2.status_code == 400
    assert response2.json()["detail"] == "Course with this title already exists"


# ==================================================
# LIST COURSES
# ==================================================
def test_list_courses(client, course):
    response = client.get("/courses/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


# ==================================================
# GET COURSE BY ID
# ==================================================
def test_get_course_success(client, course):
    response = client.get(f"/courses/{course.id}")
    assert response.status_code == 200
    assert response.json()["id"] == course.id


def test_get_course_not_found(client):
    response = client.get("/courses/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"


# ==================================================
# UPDATE COURSE
# ==================================================
def test_update_course_success(client, course, db_session):
    payload = {
        "title": "Updated Course Title",
        "price": 150.0
    }

    response = client.put(f"/courses/{course.id}", json=payload)
    assert response.status_code == 200

    db_session.refresh(course)
    assert course.title == "Updated Course Title"
    assert course.price == 150.0


def test_update_course_not_found(client):
    response = client.put("/courses/999999", json={"title": "X"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"


# ==================================================
# DELETE COURSE
# ==================================================
def test_delete_course_success(client, course, db_session):
    response = client.delete(f"/courses/{course.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Course deleted successfully"

    deleted = db_session.query(Course).filter_by(id=course.id).first()
    assert deleted is None


def test_delete_course_not_found(client):
    response = client.delete("/courses/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"
