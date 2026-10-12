from fastapi.testclient import TestClient

from app.config import Settings
from app.http_api import API_VERSION, create_app


def test_health_check_exposes_service_metadata() -> None:
    response = TestClient(
        create_app(
            settings=Settings(app_name="test-api", environment="test"),
        )
    ).get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "test-api",
        "environment": "test",
        "version": API_VERSION,
    }


def test_settings_read_http_runtime_configuration_from_environment() -> None:
    settings = Settings.from_env(
        {
            "TASK_APP_NAME": "capstone-test",
            "TASK_ENVIRONMENT": "ci",
            "TASK_CORS_ORIGINS": "https://app.example, https://admin.example",
        }
    )

    assert settings.app_name == "capstone-test"
    assert settings.environment == "ci"
    assert settings.cors_origins == ("https://app.example", "https://admin.example")


def test_versioned_item_crud_flow() -> None:
    api = TestClient(create_app())

    created = api.post(
        "/api/v1/items",
        json={"title": "FastAPI notes", "content": "Read the official docs."},
    )
    assert created.status_code == 201
    item = created.json()
    assert item["id"] == 1
    assert item["title"] == "FastAPI notes"
    assert item["content"] == "Read the official docs."
    assert item["created_at"].endswith("Z")
    assert item["updated_at"] == item["created_at"]

    listed = api.get("/api/v1/items")
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == 1

    updated = api.put("/api/v1/items/1", json={"content": "Updated notes."})
    assert updated.status_code == 200
    assert updated.json()["content"] == "Updated notes."
    assert updated.json()["created_at"] == item["created_at"]
    assert updated.json()["updated_at"] != item["updated_at"]

    deleted = api.delete("/api/v1/items/1")
    assert deleted.status_code == 204
    assert deleted.content == b""


def test_item_validation_duplicate_and_not_found_errors() -> None:
    api = TestClient(create_app())

    blank = api.post("/api/v1/items", json={"title": " "})
    assert blank.status_code == 422
    assert blank.json()["error"]["code"] == "invalid_request"

    api.post("/api/v1/items", json={"title": "Same title"})
    duplicate = api.post("/api/v1/items", json={"title": " same TITLE "})
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "duplicate_item_title"

    missing = api.get("/api/v1/items/99")
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "item_not_found"


def test_openapi_describes_health_and_versioned_items() -> None:
    schema = TestClient(create_app()).get("/openapi.json").json()

    assert schema["info"]["version"] == API_VERSION
    assert "/health" in schema["paths"]
    assert "/api/v1/items" in schema["paths"]
    assert "/api/v1/items/{item_id}" in schema["paths"]
