import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from main import app, get_session


@pytest.fixture(name="client")
def client_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def get_test_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def test_create_habit_generates_id(client):
    response = client.post("/habits", json={"title": "Drink water"})

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Drink water"
    assert data["status"] == "pending"


def test_rejects_invalid_status(client):
    response = client.post(
        "/habits",
        json={"title": "Stretch", "status": "nearly done"},
    )

    assert response.status_code == 422


def test_get_update_patch_and_delete_habit(client):
    created = client.post(
        "/habits",
        json={"title": "Read", "status": "pending"},
    ).json()

    habit_id = created["id"]

    get_response = client.get(f"/habits/{habit_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Read"

    put_response = client.put(
        f"/habits/{habit_id}",
        json={"title": "Read a chapter", "status": "completed"},
    )
    assert put_response.status_code == 200
    assert put_response.json()["id"] == habit_id
    assert put_response.json()["status"] == "completed"

    patch_response = client.patch(
        f"/habits/{habit_id}",
        json={"status": "skipped"},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["title"] == "Read a chapter"
    assert patch_response.json()["status"] == "skipped"

    delete_response = client.delete(f"/habits/{habit_id}")
    assert delete_response.status_code == 204

    missing_response = client.get(f"/habits/{habit_id}")
    assert missing_response.status_code == 404


def test_get_missing_habit_returns_404(client):
    response = client.get("/habits/999")

    assert response.status_code == 404
