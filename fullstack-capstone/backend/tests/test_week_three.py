import json
from io import StringIO

import pytest
from pydantic import ValidationError

from app.cli import main
from app.config import ConfigError, Settings
from app.logging_config import configure_logging
from app.task_models import Task, TaskValidationError
from app.task_service import TaskService
from app.task_storage import TaskDataError, TaskStorage


def test_settings_load_from_environment_and_allow_cli_overrides(task_file, monkeypatch) -> None:
    monkeypatch.setenv("TASK_DATA_FILE", str(task_file))
    monkeypatch.setenv("TASK_LOG_LEVEL", "debug")

    settings = Settings.from_env()
    overridden = settings.with_overrides(log_level="warning")

    assert settings.data_file == task_file
    assert settings.log_level == "DEBUG"
    assert overridden.log_level == "WARNING"
    assert overridden.data_file == task_file


def test_settings_reject_unknown_log_level() -> None:
    with pytest.raises(ConfigError, match="unsupported log level"):
        Settings(log_level="verbose")


def test_task_model_is_strict_and_normalizes_title() -> None:
    task = Task(id=1, title="  Read docs  ")

    assert task.title == "Read docs"
    with pytest.raises(ValidationError):
        Task(id="1", title="Read docs")


def test_service_rejects_blank_title_with_domain_error(task_file) -> None:
    with pytest.raises(TaskValidationError, match="cannot be empty"):
        TaskService(TaskStorage(task_file)).add_task("   ")


def test_invalid_persisted_record_has_location_and_error_code(task_file) -> None:
    task_file.write_text(
        json.dumps([{"id": 1, "title": "Missing completion field"}]),
        encoding="utf-8",
    )

    with pytest.raises(TaskDataError, match="completed") as error:
        TaskStorage(task_file).load()

    assert error.value.as_dict()["code"] == "task_data_error"


def test_structured_logs_include_event_and_context(task_file) -> None:
    stream = StringIO()
    configure_logging("DEBUG", stream=stream)
    TaskService(TaskStorage(task_file)).add_task("Log this task")

    records = [json.loads(line) for line in stream.getvalue().splitlines()]
    created = next(record for record in records if record["event"] == "task_created")
    assert created["context"]["task_id"] == 1


def test_cli_error_contract_has_stable_code(task_file, capsys) -> None:
    exit_code = main(["--data-file", str(task_file), "add", "   "])

    assert exit_code == 1
    assert "Error [invalid_task]" in capsys.readouterr().err
