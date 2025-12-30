import pytest
from fastapi import status

# ---------------- CREATE ----------------
def test_create_quiz_history(client, user, checkpoint, video, course):
    payload = {
        "user_id": user.id,
        "checkpoint_id": checkpoint.id,
        "course_id": course.id,
        "video_id": video.id,
        "answer": "My Answer",
        "result": True,
        "question": "What is testing?"
    }

    response = client.post("/quiz-history/", json=payload)
    print("RESPONSE JSON:", response.json())
    print("RESPONSE STATUS:", response.status_code)

    assert response.status_code == status.HTTP_201_CREATED



# ---------------- GET ALL ----------------
def test_get_all_quiz_histories(client, quiz_history):
    response = client.get("/quiz-history/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert any(h["id"] == quiz_history.id for h in data)

# ---------------- GET BY USER ----------------
def test_get_user_quiz_history(client, user, quiz_history):
    response = client.get(f"/quiz-history/user/{user.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(h["user_id"] == user.id for h in data)

# ---------------- GET BY ID ----------------
def test_get_quiz_history_by_id(client, quiz_history):
    response = client.get(f"/quiz-history/{quiz_history.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == quiz_history.id

# ---------------- UPDATE ----------------
def test_update_quiz_history(client, quiz_history, user, checkpoint, video, course):
    payload = {
        "user_id": user.id,
        "checkpoint_id": checkpoint.id,
        "course_id": course.id,
        "video_id": video.id,
        "answer": "Updated Answer",
        "result": False,
        "question": "Updated Question?"
    }

    response = client.put(f"/quiz-history/{quiz_history.id}", json=payload)
    print("RESPONSE JSON:", response.json())
    print("RESPONSE STATUS:", response.status_code)

    assert response.status_code == status.HTTP_200_OK


# ---------------- DELETE ----------------
def test_delete_quiz_history(client, quiz_history):
    response = client.delete(f"/quiz-history/{quiz_history.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT