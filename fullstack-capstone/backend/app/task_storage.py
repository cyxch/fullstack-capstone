"""JSON file persistence for the task list."""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Sequence
from pathlib import Path

from .logging_config import context_from_mapping, get_logger
from .task_models import Task, TaskValidationError

logger = get_logger("task_storage")


class TaskDataError(ValueError):
    """Raised when the task file cannot be read as valid task data."""

    code = "task_data_error"

    def as_dict(self) -> dict[str, str]:
        """Return the stable error contract used by CLI adapters."""

        return {"code": self.code, "message": str(self)}


class TaskStorage:
    """Read and write a validated list of tasks from a JSON file."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load(self) -> list[Task]:
        """Load tasks, treating a missing file as an empty task list."""

        if not self.path.exists():
            return []
        if not self.path.is_file():
            raise TaskDataError(f"task path is not a file: {self.path}")

        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise TaskDataError(f"invalid JSON in {self.path}: {exc.msg}") from exc
        except UnicodeDecodeError as exc:
            raise TaskDataError(f"invalid UTF-8 in {self.path}: {exc.reason}") from exc
        except OSError as exc:
            raise TaskDataError(f"cannot read task file {self.path}: {exc}") from exc

        if not isinstance(payload, list):
            raise TaskDataError("task file must contain a JSON array")

        tasks: list[Task] = []
        seen_ids: set[int] = set()
        seen_titles: set[str] = set()
        for index, item in enumerate(payload):
            try:
                task = Task.model_validate_record(item)
            except TaskValidationError as exc:
                raise TaskDataError(f"invalid task at index {index}: {exc}") from exc

            title_key = task.title.casefold()
            if task.id in seen_ids:
                raise TaskDataError(f"duplicate task id in file: {task.id}")
            if title_key in seen_titles:
                raise TaskDataError(f"duplicate task title in file: {task.title}")
            seen_ids.add(task.id)
            seen_titles.add(title_key)
            tasks.append(task)
        logger.debug(
            "tasks loaded",
            extra=context_from_mapping(
                {"event": "tasks_loaded", "count": len(tasks), "path": str(self.path)}
            ),
        )
        return tasks

    def save(self, tasks: Sequence[Task]) -> None:
        """Persist tasks atomically so an interrupted write cannot corrupt JSON."""

        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(
            [task.to_dict() for task in tasks],
            ensure_ascii=False,
            indent=2,
        )
        temporary_path: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.path.parent,
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                temporary_path = temporary_file.name
                temporary_file.write(payload)
                temporary_file.write("\n")
                temporary_file.flush()
                os.fsync(temporary_file.fileno())
            os.replace(temporary_path, self.path)
            temporary_path = None
            logger.debug(
                "tasks saved",
                extra=context_from_mapping(
                    {"event": "tasks_saved", "count": len(tasks), "path": str(self.path)}
                ),
            )
        except OSError as exc:
            raise TaskDataError(f"cannot write task file {self.path}: {exc}") from exc
        finally:
            if temporary_path is not None:
                try:
                    os.unlink(temporary_path)
                except OSError:
                    pass
