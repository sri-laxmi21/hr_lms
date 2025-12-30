from app.models.video_m import Video
from app.models.course_m import Course

# ==================================================
# CREATE VIDEO
# ==================================================
def test_create_video_success(client, course, db_session):
    payload = {
        "title": "New Video",
        "description": "Intro video",
        "youtube_url": "https://youtube.com/watch?v=test123",
        "duration": 15.0,
        "course_id": course.id
    }

    response = client.post("/videos/", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "New Video"
    assert data["duration"] == 15.0
    assert data["course_id"] == course.id

    video = db_session.query(Video).filter_by(title="New Video").first()
    assert video is not None

    db_session.refresh(course)
    assert course.duration == 15.0


# ==================================================
# CREATE VIDEO – COURSE NOT FOUND
# ==================================================
def test_create_video_course_not_found(client):
    payload = {
        "title": "Invalid",
        "description": "test",
        "youtube_url": "https://youtube.com/watch?v=invalid",
        "duration": 5.0,
        "course_id": 999999
    }

    response = client.post("/videos/", json=payload)
    assert response.status_code == 404


# ==================================================
# LIST VIDEOS
# ==================================================
def test_list_videos(client, video):
    response = client.get("/videos/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ==================================================
# GET VIDEO BY ID
# ==================================================
def test_get_video_by_id_success(client, video):
    response = client.get(f"/videos/{video.id}")
    assert response.status_code == 200
    assert response.json()["id"] == video.id


def test_get_video_not_found(client):
    response = client.get("/videos/999999")
    assert response.status_code == 404


# ==================================================
# UPDATE VIDEO
# ==================================================
def test_update_video_success(client, video, db_session):
    payload = {
        "title": "Updated Title",
        "duration": 20.0
    }

    response = client.put(f"/videos/{video.id}", json=payload)
    assert response.status_code == 200

    db_session.refresh(video)
    assert video.title == "Updated Title"
    assert video.duration == 20.0

    course = db_session.query(Course).filter_by(id=video.course_id).first()
    assert course.duration == 20.0


def test_update_video_not_found(client):
    response = client.put(
        "/videos/999999",
        json={"title": "X", "duration": 5.0}
    )
    assert response.status_code == 404


# ==================================================
# DELETE VIDEO
# ==================================================
def test_delete_video_success(client, video, db_session):
    response = client.delete(f"/videos/{video.id}")
    assert response.status_code == 204

    deleted = db_session.query(Video).filter_by(id=video.id).first()
    assert deleted is None


def test_delete_video_not_found(client):
    response = client.delete("/videos/999999")
    assert response.status_code == 404
