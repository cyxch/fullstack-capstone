from fastapi.testclient import TestClient

from app.http_api import create_app


def client() -> TestClient:
    return TestClient(create_app())


def test_task_crud_flow_uses_rest_status_codes() -> None:
    api = client()

    created = api.post("/tasks", json={"title": "Learn HTTP"})
    assert created.status_code == 201
    assert created.json() == {"id": 1, "title": "Learn HTTP", "completed": False}

    listed = api.get("/tasks", params={"status": "pending"})
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == 1

    updated = api.put("/tasks/1", json={"completed": True})
    assert updated.status_code == 200
    assert updated.json()["completed"] is True

    deleted = api.delete("/tasks/1")
    assert deleted.status_code == 204
    assert deleted.content == b""


def test_get_unknown_task_returns_json_404() -> None:
    response = client().get("/tasks/99")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "task_not_found"


def test_duplicate_title_returns_json_409() -> None:
    api = client()
    api.post("/tasks", json={"title": "Same title"})

    response = api.post("/tasks", json={"title": " same TITLE "})

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "duplicate_task"


def test_missing_title_returns_json_422() -> None:
    response = client().post("/tasks", json={})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"


def test_blank_update_title_returns_json_422() -> None:
    response = client().put("/tasks/1", json={"title": " "})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"


def test_invalid_status_and_cors_are_visible_to_clients() -> None:
    api = client()

    invalid = api.get("/tasks", params={"status": "blocked"})
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "invalid_request"

    preflight = api.options(
        "/tasks",
        headers={
            "Origin": "https://example.test",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert preflight.status_code == 200
    assert preflight.headers["access-control-allow-origin"] == "*"


def test_openapi_docs_are_available() -> None:
    response = client().get("/docs")

    assert response.status_code == 200
    assert "Task HTTP API" in response.text
