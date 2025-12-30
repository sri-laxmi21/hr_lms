import pytest
from app.models.category_m import Category
from app.main import app

# ============================
# PERMISSION OVERRIDES
# ============================
@pytest.fixture(autouse=True)
def override_permissions():
    def allow_all():
        return {"id": 1, "role": "admin"}

    app.dependency_overrides = {
        # create
        app.dependency_overrides.get: None
    }

    from app.permission_dependencies import (
        require_view_permission,
        require_create_permission,
        require_edit_permission,
        require_delete_permission,
    )

    app.dependency_overrides[require_view_permission] = lambda *args, **kwargs: allow_all()
    app.dependency_overrides[require_create_permission] = lambda *args, **kwargs: allow_all()
    app.dependency_overrides[require_edit_permission] = lambda *args, **kwargs: allow_all()
    app.dependency_overrides[require_delete_permission] = lambda *args, **kwargs: allow_all()

    yield
    app.dependency_overrides = {}


# ============================
# FIXTURES
# ============================
@pytest.fixture
def category(db_session):
    category = Category(name="Programming")
    db_session.add(category)
    db_session.flush()
    return category


# ============================
# CREATE CATEGORY
# ============================
def test_create_category_success(client, db_session):
    payload = {
        "name": "Design"
    }

    response = client.post("/categories/", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Design"
    assert data["courses"] == []

    category = db_session.query(Category).filter_by(name="Design").first()
    assert category is not None


def test_create_category_duplicate(client, category):
    payload = {
        "name": "Programming"
    }

    response = client.post("/categories/", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Category already exists"


# ============================
# LIST CATEGORIES
# ============================
def test_list_categories(client, category):
    response = client.get("/categories/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["name"] == "Programming"


# ============================
# GET CATEGORY BY ID
# ============================
def test_get_category_success(client, category):
    response = client.get(f"/categories/{category.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == category.id
    assert data["name"] == "Programming"


def test_get_category_not_found(client):
    response = client.get("/categories/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


# ============================
# UPDATE CATEGORY
# ============================
def test_update_category_success(client, category, db_session):
    payload = {
        "name": "Updated Programming"
    }

    response = client.put(f"/categories/{category.id}", json=payload)
    assert response.status_code == 200

    db_session.refresh(category)
    assert category.name == "Updated Programming"


def test_update_category_not_found(client):
    response = client.put(
        "/categories/999999",
        json={"name": "Invalid"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


# ============================
# DELETE CATEGORY
# ============================
def test_delete_category_success(client, category, db_session):
    response = client.delete(f"/categories/{category.id}")
    assert response.status_code == 204

    deleted = db_session.query(Category).filter_by(id=category.id).first()
    assert deleted is None


def test_delete_category_not_found(client):
    response = client.delete("/categories/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"
