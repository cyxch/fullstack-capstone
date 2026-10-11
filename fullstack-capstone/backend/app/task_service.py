"""Business rules for creating and managing tasks."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal, Protocol

from .logging_config import context_from_mapping, get_logger
from .task_models import Task, TaskCreate, TaskQuery, TaskValidationError


class TaskStore(Protocol):
    """Persistence operations required by the task service."""

    def load(self) -> list[Task]:
        """Load the current task snapshot."""

    def save(self, tasks: Sequence[Task]) -> None:
        """Persist a task snapshot."""


TaskStatus = Literal["all", "pending", "completed"]
logger = get_logger("task_service")


class TaskError(Exception):
    """Base class for expected task-list errors."""

    code = "task_error"

    def as_dict(self) -> dict[str, str]:
        """Return the stable error contract used by CLI adapters."""

        return {"code": self.code, "message": str(self)}


class DuplicateTaskError(TaskError):
    """Raised when a task title already exists."""

    code = "duplicate_task"


class TaskNotFoundError(TaskError):
    """Raised when an operation references an unknown task id."""

    code = "task_not_found"


class TaskService:
    """Apply task rules while delegating persistence to ``TaskStorage``."""

    def __init__(self, storage: TaskStore) -> None:
        self.storage = storage

    def add_task(self, title: str) -> Task:
        """Create and persist a pending task with a unique title."""

        request = TaskCreate.model_validate_title(title)
        candidate = request.title
        tasks = self.storage.load()
        if any(task.title.casefold() == candidate.casefold() for task in tasks):
            raise DuplicateTaskError(f"task already exists: {candidate}")

        next_id = max((task.id for task in tasks), default=0) + 1
        task = Task(id=next_id, title=request.title)
        self.storage.save([*tasks, task])
        logger.info(
            "task created",
            extra=context_from_mapping({"event": "task_created", "task_id": task.id}),
        )
        return task

    def list_tasks(
        self,
        *,
        status: TaskStatus = "all",
        keyword: str | None = None,
    ) -> list[Task]:
        """Return tasks filtered by completion state and optional title keyword."""

        query = TaskQuery.model_validate_query(status=status, keyword=keyword)
        tasks = self.storage.load()
        if query.status == "pending":
            tasks = [task for task in tasks if not task.completed]
        elif query.status == "completed":
            tasks = [task for task in tasks if task.completed]
        if query.keyword:
            normalized_keyword = query.keyword.casefold()
            tasks = [task for task in tasks if normalized_keyword in task.title.casefold()]
        logger.debug(
            "tasks queried",
            extra=context_from_mapping(
                {"event": "tasks_queried", "count": len(tasks), "status": query.status}
            ),
        )
        return tasks

    def complete_task(self, task_id: int) -> Task:
        """Mark a task complete and persist the updated list."""

        self._validate_task_id(task_id)
        tasks = self.storage.load()
        for index, task in enumerate(tasks):
            if task.id == task_id:
                completed = Task(id=task.id, title=task.title, completed=True)
                tasks[index] = completed
                self.storage.save(tasks)
                logger.info(
                    "task completed",
                    extra=context_from_mapping({"event": "task_completed", "task_id": task.id}),
                )
                return completed
        raise TaskNotFoundError(f"task not found: {task_id}")

    def delete_task(self, task_id: int) -> Task:
        """Delete a task and return the removed value."""

        self._validate_task_id(task_id)
        tasks = self.storage.load()
        for index, task in enumerate(tasks):
            if task.id == task_id:
                removed = tasks.pop(index)
                self.storage.save(tasks)
                logger.info(
                    "task deleted",
                    extra=context_from_mapping({"event": "task_deleted", "task_id": removed.id}),
                )
                return removed
        raise TaskNotFoundError(f"task not found: {task_id}")

    def get_task(self, task_id: int) -> Task:
        """Return one task or raise the stable not-found domain error."""

        self._validate_task_id(task_id)
        for task in self.storage.load():
            if task.id == task_id:
                return task
        raise TaskNotFoundError(f"task not found: {task_id}")

    def update_task(
        self,
        task_id: int,
        *,
        title: str | None = None,
        completed: bool | None = None,
    ) -> Task:
        """Update supplied fields while enforcing the same task rules as create."""

        self._validate_task_id(task_id)
        if title is None and completed is None:
            raise TaskValidationError("at least one task field is required")
        validated_title = (
            TaskCreate.model_validate_title(title).title if title is not None else None
        )
        if completed is not None and not isinstance(completed, bool):
            raise TaskValidationError("completed must be a boolean")

        tasks = self.storage.load()
        for index, task in enumerate(tasks):
            if task.id != task_id:
                continue
            next_title = validated_title if validated_title is not None else task.title
            if any(
                candidate.id != task_id and candidate.title.casefold() == next_title.casefold()
                for candidate in tasks
            ):
                raise DuplicateTaskError(f"task already exists: {next_title}")
            updated = Task(
                id=task.id,
                title=next_title,
                completed=completed if completed is not None else task.completed,
            )
            tasks[index] = updated
            self.storage.save(tasks)
            logger.info(
                "task updated",
                extra=context_from_mapping({"event": "task_updated", "task_id": updated.id}),
            )
            return updated
        raise TaskNotFoundError(f"task not found: {task_id}")

    @staticmethod
    def _validate_task_id(task_id: int) -> None:
        if isinstance(task_id, bool) or not isinstance(task_id, int) or task_id < 1:
            raise TaskValidationError("task id must be a positive integer")
