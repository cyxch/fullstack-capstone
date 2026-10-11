"""Command-line interface for the JSON-backed task list."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .task_service import (
    DuplicateTaskError,
    TaskError,
    TaskNotFoundError,
    TaskService,
)
from .task_storage import TaskDataError, TaskStorage

DEFAULT_DATA_FILE = Path("data/tasks.json")


def positive_int(value: str) -> int:
    """Parse a positive integer for task ids."""

    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if number < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser without performing any file I/O."""

    parser = argparse.ArgumentParser(description="Manage a small JSON-backed task list.")
    parser.add_argument(
        "--data-file",
        type=Path,
        default=None,
        help=f"JSON storage path (default: {DEFAULT_DATA_FILE})",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="create a task")
    add_parser.add_argument("title", help="task title")
    add_parser.add_argument("--data-file", type=Path, default=argparse.SUPPRESS)

    complete_parser = subparsers.add_parser("complete", help="mark a task complete")
    complete_parser.add_argument("task_id", type=positive_int)
    complete_parser.add_argument("--data-file", type=Path, default=argparse.SUPPRESS)

    delete_parser = subparsers.add_parser("delete", help="delete a task")
    delete_parser.add_argument("task_id", type=positive_int)
    delete_parser.add_argument("--data-file", type=Path, default=argparse.SUPPRESS)

    query_parser = subparsers.add_parser(
        "query",
        aliases=["list"],
        help="query tasks",
    )
    query_parser.add_argument(
        "--status",
        choices=("all", "pending", "completed"),
        default="all",
    )
    query_parser.add_argument("--keyword")
    query_parser.add_argument("--data-file", type=Path, default=argparse.SUPPRESS)
    return parser


def _print_tasks(tasks: list) -> None:
    if not tasks:
        print("No tasks found.")
        return
    for task in tasks:
        marker = "x" if task.completed else " "
        print(f"[{marker}] {task.id}: {task.title}")


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process-style exit code."""

    parser = build_parser()
    args = parser.parse_args(argv)
    data_file = args.data_file or DEFAULT_DATA_FILE
    service = TaskService(TaskStorage(data_file))

    try:
        if args.command == "add":
            task = service.add_task(args.title)
            print(f"Added task {task.id}: {task.title}")
        elif args.command == "complete":
            task = service.complete_task(args.task_id)
            print(f"Completed task {task.id}: {task.title}")
        elif args.command == "delete":
            task = service.delete_task(args.task_id)
            print(f"Deleted task {task.id}: {task.title}")
        else:
            _print_tasks(service.list_tasks(status=args.status, keyword=args.keyword))
    except (DuplicateTaskError, TaskNotFoundError, TaskDataError, TaskError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
