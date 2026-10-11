from __future__ import annotations

import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest


@pytest.fixture
def task_file() -> Iterator[Path]:
    """Use a workspace-local file because managed temporary directories are restricted."""

    path = Path.cwd() / f".task-test-{uuid.uuid4().hex}.json"
    try:
        yield path
    finally:
        path.unlink(missing_ok=True)
