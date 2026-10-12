"""Small in-memory REST API used to practice HTTP and JSON contracts."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Annotated, Literal

from fastapi import APIRouter, FastAPI, Path, Query, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import Settings
from .item_models import Item, ItemCreate, ItemUpdate, ItemValidationError
from .item_service import (
    DuplicateItemTitleError,
    ItemError,
    ItemNotFoundError,
    ItemService,
    ItemStore,
)
from .item_storage import InMemoryItemStorage
from .task_models import Task, TaskCreate, TaskUpdate, TaskValidationError
from .task_service import (
    DuplicateTaskError,
    TaskError,
    TaskNotFoundError,
    TaskService,
    TaskStore,
)
from .task_storage import InMemoryTaskStorage

TaskStatus = Literal["all", "pending", "completed"]
TaskId = Annotated[int, Path(gt=0, description="Positive task identifier")]
ItemId = Annotated[int, Path(gt=0, description="Positive item identifier")]
API_VERSION = "0.7.0"


def _error_payload(code: str, message: str, *, details: object | None = None) -> dict[str, object]:
    """Build the stable JSON error envelope returned by this API."""

    error: dict[str, object] = {"code": code, "message": message}
    if details is not None:
        error["details"] = details
    return {"error": error}


def _domain_error_response(
    error: TaskError | TaskValidationError | ItemError | ItemValidationError,
) -> JSONResponse:
    """Map expected domain failures to an HTTP status and JSON error body."""

    if isinstance(error, (DuplicateTaskError, DuplicateItemTitleError)):
        http_status = status.HTTP_409_CONFLICT
    elif isinstance(error, (TaskNotFoundError, ItemNotFoundError)):
        http_status = status.HTTP_404_NOT_FOUND
    else:
        http_status = 422
    return JSONResponse(
        status_code=http_status,
        content=_error_payload(error.code, str(error)),
    )


def create_app(
    storage: TaskStore | None = None,
    *,
    allow_origins: Sequence[str] | None = None,
    item_storage: ItemStore | None = None,
    settings: Settings | None = None,
) -> FastAPI:
    """Create an isolated API instance backed by memory by default."""

    runtime_settings = settings or Settings.from_env()
    service = TaskService(storage or InMemoryTaskStorage())
    item_service = ItemService(item_storage or InMemoryItemStorage())
    application = FastAPI(
        title="Task HTTP API - Capstone",
        version=API_VERSION,
        description="Learning API for the Python full-stack capstone project.",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(allow_origins or runtime_settings.cors_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type"],
    )

    @application.exception_handler(RequestValidationError)
    async def request_validation_handler(
        request: Request,
        error: RequestValidationError,
    ) -> JSONResponse:
        del request
        return JSONResponse(
            status_code=422,
            content=_error_payload(
                "invalid_request",
                "request validation failed",
                details=jsonable_encoder(error.errors()),
            ),
        )

    @application.exception_handler(TaskValidationError)
    async def task_validation_handler(request: Request, error: TaskValidationError) -> JSONResponse:
        del request
        return _domain_error_response(error)

    @application.exception_handler(TaskError)
    async def task_error_handler(request: Request, error: TaskError) -> JSONResponse:
        del request
        return _domain_error_response(error)

    @application.exception_handler(ItemError)
    async def item_error_handler(request: Request, error: ItemError) -> JSONResponse:
        del request
        return _domain_error_response(error)

    @application.exception_handler(ItemValidationError)
    async def item_validation_handler(
        request: Request,
        error: ItemValidationError,
    ) -> JSONResponse:
        del request
        return _domain_error_response(error)

    @application.get(
        "/health",
        tags=["system"],
        summary="Check API health",
    )
    def health() -> dict[str, str]:
        """Return a lightweight liveness response for local and CI checks."""

        return {
            "status": "ok",
            "service": runtime_settings.app_name,
            "environment": runtime_settings.environment,
            "version": API_VERSION,
        }

    items_router = APIRouter(prefix="/api/v1/items", tags=["items"])

    @items_router.get("", response_model=list[Item], summary="List items")
    def list_items() -> list[Item]:
        """Return all knowledge items in insertion order."""

        return item_service.list_items()

    @items_router.get("/{item_id}", response_model=Item, summary="Get one item")
    def get_item(item_id: ItemId) -> Item:
        """Return one item by its positive numeric id."""

        return item_service.get_item(item_id)

    @items_router.post(
        "",
        response_model=Item,
        status_code=status.HTTP_201_CREATED,
        summary="Create an item",
    )
    def create_item(payload: ItemCreate) -> Item:
        """Create a knowledge item with a title and optional content."""

        return item_service.create_item(payload)

    @items_router.put("/{item_id}", response_model=Item, summary="Update an item")
    def update_item(item_id: ItemId, payload: ItemUpdate) -> Item:
        """Update one or both mutable item fields."""

        return item_service.update_item(item_id, payload)

    @items_router.delete(
        "/{item_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        summary="Delete an item",
    )
    def delete_item(item_id: ItemId) -> Response:
        """Delete one item and return an empty 204 response."""

        item_service.delete_item(item_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    application.include_router(items_router)

    @application.get(
        "/tasks",
        response_model=list[Task],
        summary="List tasks",
    )
    def list_tasks(
        task_status: Annotated[TaskStatus, Query(alias="status")] = "all",
        keyword: Annotated[str | None, Query(max_length=100)] = None,
    ) -> list[Task]:
        """List all tasks or filter by completion state and title keyword."""

        return service.list_tasks(status=task_status, keyword=keyword)

    @application.get(
        "/tasks/{task_id}",
        response_model=Task,
        summary="Get one task",
    )
    def get_task(task_id: TaskId) -> Task:
        """Return one task by its numeric id."""

        return service.get_task(task_id)

    @application.post(
        "/tasks",
        response_model=Task,
        status_code=status.HTTP_201_CREATED,
        summary="Create a task",
    )
    def create_task(payload: TaskCreate) -> Task:
        """Create a pending task and return its representation."""

        return service.add_task(payload.title)

    @application.put(
        "/tasks/{task_id}",
        response_model=Task,
        summary="Update a task",
    )
    def update_task(task_id: TaskId, payload: TaskUpdate) -> Task:
        """Update one or both mutable task fields."""

        return service.update_task(
            task_id,
            title=payload.title,
            completed=payload.completed,
        )

    @application.delete(
        "/tasks/{task_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        summary="Delete a task",
    )
    def delete_task(task_id: TaskId) -> Response:
        """Delete a task and return the standard empty 204 response."""

        service.delete_task(task_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return application


app = create_app()


if __name__ == "__main__":  # pragma: no cover - manual uvicorn entry point
    import uvicorn

    uvicorn.run("app.http_api:app", host="127.0.0.1", port=8000, reload=False)
