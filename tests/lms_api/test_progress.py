import pytest
from fastapi import status
from app.models.Progress_m import Progress

MENU_ID = 37

# -------------------- CREATE / UPDATE PROGRESS --------------------
def test_create_progress(client, user, course):
    response = client.post(
        f"/progress/{course.id}/watch",
        params={"watched_minutes": 30, "user_id": user.id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["watched_minutes"] == 30
    assert data["progress_percentage"] == 25  # 30/120*100

def test_update_progress(client, user, course, progress):
    response = client.post(
        f"/progress/{course.id}/watch",
        params={"watched_minutes": 90, "user_id": user.id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["watched_minutes"] == 90
    assert data["progress_percentage"] == 75  # 90/120*100

def test_progress_exceeds_course_duration(client, user, course):
    response = client.post(
        f"/progress/{course.id}/watch",
        params={"watched_minutes": 200, "user_id": user.id}
    )
    assert response.status_code == 400
    assert "cannot exceed course duration" in response.json()["detail"]

def test_course_not_found(client, user):
    response = client.post(
        "/progress/999/watch",
        params={"watched_minutes": 10, "user_id": user.id}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"

# -------------------- GET ALL PROGRESS --------------------
def test_list_progress(client, progress):
    response = client.get("/progress/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_list_progress_filter_user(client, user, progress):
    response = client.get(f"/progress/?user_id={user.id}")
    assert response.status_code == 200
    data = response.json()
    for p in data:
        assert p["user_id"] == user.id

# -------------------- DELETE PROGRESS --------------------
def test_delete_progress(client, user, course, progress):
    response = client.delete(f"/progress/{course.id}/user/{user.id}")
    assert response.status_code == 204
    # Ensure it's deleted
    get_response = client.get(f"/progress/?user_id={user.id}&course_id={course.id}")
    assert len(get_response.json()) == 0

def test_delete_nonexistent_progress(client):
    response = client.delete("/progress/999/user/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Progress not found"
