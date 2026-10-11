"""Data model and validation for persisted tasks."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


class TaskValidationError(ValueError):
    """Raised when a task does not satisfy the storage contract."""


@dataclass(frozen=True, slots=True)
class Task:
    """A task stored by the command-line application."""

    id: int
    title: str
    completed: bool = False

    def __post_init__(self) -> None:
        if isinstance(self.id, bool) or not isinstance(self.id, int) or self.id < 1:
            raise TaskValidationError("task id must be a positive integer")
        if not isinstance(self.title, str):
            raise TaskValidationError("task title must be a string")
        title = self.title.strip()
        if not title:
            raise TaskValidationError("task title cannot be empty")
        if not isinstance(self.completed, bool):
            raise TaskValidationError("task completed must be a boolean")
        object.__setattr__(self, "title", title)

    def to_dict(self) -> dict[str, Any]:
        """Return the JSON-compatible representation of this task."""

        return asdict(self)

    @classmethod
    def from_dict(cls, payload: object) -> Task:
        """Build a task from a JSON object and validate every field."""

        if not isinstance(payload, dict):
            raise TaskValidationError("each task must be a JSON object")

        required = {"id", "title", "completed"}
        if set(payload) != required:
            raise TaskValidationError("task fields must be exactly id, title, and completed")

        return cls(
            id=payload["id"],
            title=payload["title"],
            completed=payload["completed"],
        )
