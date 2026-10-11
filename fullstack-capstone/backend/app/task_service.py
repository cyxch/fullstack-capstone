"""Business rules for creating and managing tasks."""

from __future__ import annotations

from typing import Literal

from .task_models import Task, TaskValidationError
from .task_storage import TaskStorage

TaskStatus = Literal["all", "pending", "completed"]


class TaskError(Exception):
    """Base class for expected task-list errors."""


class DuplicateTaskError(TaskError):
    """Raised when a task title already exists."""


class TaskNotFoundError(TaskError):
    """Raised when an operation references an unknown task id."""


class TaskService:
    """Apply task rules while delegating persistence to ``TaskStorage``."""

    def __init__(self, storage: TaskStorage) -> None:
        self.storage = storage

    def add_task(self, title: str) -> Task:
        """Create and persist a pending task with a unique title."""

        if not isinstance(title, str):
            raise TaskValidationError("task title must be a string")
        candidate = title.strip()
        tasks = self.storage.load()
        if any(task.title.casefold() == candidate.casefold() for task in tasks):
            raise DuplicateTaskError(f"task already exists: {candidate}")

        next_id = max((task.id for task in tasks), default=0) + 1
        task = Task(id=next_id, title=title)
        self.storage.save([*tasks, task])
        return task

    def list_tasks(
        self,
        *,
        status: TaskStatus = "all",
        keyword: str | None = None,
    ) -> list[Task]:
        """Return tasks filtered by completion state and optional title keyword."""

        if status not in {"all", "pending", "completed"}:
            raise ValueError(f"unsupported task status: {status}")
        tasks = self.storage.load()
        if status == "pending":
            tasks = [task for task in tasks if not task.completed]
        elif status == "completed":
            tasks = [task for task in tasks if task.completed]
        if keyword:
            normalized_keyword = keyword.casefold()
            tasks = [task for task in tasks if normalized_keyword in task.title.casefold()]
        return tasks

    def complete_task(self, task_id: int) -> Task:
        """Mark a task complete and persist the updated list."""

        tasks = self.storage.load()
        for index, task in enumerate(tasks):
            if task.id == task_id:
                completed = Task(id=task.id, title=task.title, completed=True)
                tasks[index] = completed
                self.storage.save(tasks)
                return completed
        raise TaskNotFoundError(f"task not found: {task_id}")

    def delete_task(self, task_id: int) -> Task:
        """Delete a task and return the removed value."""

        tasks = self.storage.load()
        for index, task in enumerate(tasks):
            if task.id == task_id:
                removed = tasks.pop(index)
                self.storage.save(tasks)
                return removed
        raise TaskNotFoundError(f"task not found: {task_id}")
