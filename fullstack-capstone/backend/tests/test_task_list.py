import json

import pytest

from app.cli import main
from app.task_service import DuplicateTaskError, TaskNotFoundError, TaskService
from app.task_storage import TaskDataError, TaskStorage


def service_for(task_file) -> TaskService:
    return TaskService(TaskStorage(task_file))


def test_add_task_persists_json(task_file) -> None:
    service = service_for(task_file)

    task = service.add_task("Read Python docs")

    assert task.id == 1
    assert service.list_tasks() == [task]
    assert json.loads(task_file.read_text(encoding="utf-8")) == [
        {"id": 1, "title": "Read Python docs", "completed": False}
    ]


def test_duplicate_title_is_rejected_case_insensitively(task_file) -> None:
    service = service_for(task_file)
    service.add_task("Write tests")

    with pytest.raises(DuplicateTaskError):
        service.add_task(" write TESTS ")


def test_complete_task_and_query_by_status(task_file) -> None:
    service = service_for(task_file)
    task = service.add_task("Finish exercise")

    completed = service.complete_task(task.id)

    assert completed.completed is True
    assert service.list_tasks(status="pending") == []
    assert service.list_tasks(status="completed") == [completed]


def test_delete_task_persists_empty_list(task_file) -> None:
    service = service_for(task_file)
    task = service.add_task("Temporary task")

    assert service.delete_task(task.id) == task
    assert service.list_tasks() == []
    assert json.loads(task_file.read_text(encoding="utf-8")) == []


def test_unknown_task_id_is_rejected(task_file) -> None:
    service = service_for(task_file)

    with pytest.raises(TaskNotFoundError):
        service.complete_task(99)


def test_missing_file_is_an_empty_list(task_file) -> None:
    assert TaskStorage(task_file).load() == []


def test_empty_file_and_invalid_json_are_rejected(task_file) -> None:
    path = task_file
    path.write_text("", encoding="utf-8")
    with pytest.raises(TaskDataError):
        TaskStorage(path).load()

    path.write_text("{not-json", encoding="utf-8")
    with pytest.raises(TaskDataError):
        TaskStorage(path).load()


def test_cli_supports_add_query_complete_and_delete(task_file, capsys) -> None:
    data_file = task_file
    assert main(["--data-file", str(data_file), "add", "CLI task"]) == 0
    assert main(["--data-file", str(data_file), "query"]) == 0
    assert main(["--data-file", str(data_file), "complete", "1"]) == 0
    assert main(["--data-file", str(data_file), "delete", "1"]) == 0

    output = capsys.readouterr().out
    assert "Added task 1: CLI task" in output
    assert "[ ] 1: CLI task" in output
    assert "Completed task 1: CLI task" in output
    assert "Deleted task 1: CLI task" in output
