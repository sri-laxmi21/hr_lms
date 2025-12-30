from fastapi import status


# ---------------- CREATE ----------------
def test_create_checkpoint(client, course, video):
    payload = {
        "course_id": course.id,
        "video_id": video.id,
        "timestamp": 10.0,
        "question": "What is FastAPI?",
        "choices": "Framework,Database,Language,Tool",
        "correct_answer": "Framework",
        "required": True
    }

    response = client.post("/checkpoints/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["question"] == payload["question"]
    assert data["choices"] == payload["choices"]


# ---------------- LIST ----------------
def test_list_checkpoints(client, checkpoint):
    response = client.get("/checkpoints/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) >= 1


# ---------------- GET BY ID ----------------
def test_get_checkpoint_by_id(client, checkpoint):
    response = client.get(f"/checkpoints/{checkpoint.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == checkpoint.id


# ---------------- UPDATE ----------------
def test_update_checkpoint(client, checkpoint):
    payload = {
        "course_id": checkpoint.course_id,
        "video_id": checkpoint.video_id,
        "timestamp": checkpoint.timestamp,
        "question": "Updated Question",
        "choices": "A,B,C,D",
        "correct_answer": "A",
        "required": checkpoint.required
    }

    response = client.put(f"/checkpoints/{checkpoint.id}", json=payload)

    print("RESPONSE JSON:", response.json())
    print("RESPONSE STATUS:", response.status_code)

    assert response.status_code == status.HTTP_200_OK


# ---------------- DELETE ----------------
def test_delete_checkpoint(client, checkpoint):
    response = client.delete(f"/checkpoints/{checkpoint.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify deleted
    get_response = client.get(f"/checkpoints/{checkpoint.id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND
