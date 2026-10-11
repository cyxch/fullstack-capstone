"""Structured logging setup shared by the CLI and service modules."""

from __future__ import annotations

import json
import logging
import sys
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import TextIO

from .config import normalize_log_level

LOGGER_NAME = "fullstack_capstone"
_CONTEXT_FIELDS = ("event", "task_id", "count", "path", "status", "keyword", "error_type")


class JsonFormatter(logging.Formatter):
    """Format each record as one JSON object suitable for log aggregation."""

    def format(self, record: logging.LogRecord) -> str:
        context: dict[str, object] = {}
        for field in _CONTEXT_FIELDS:
            if hasattr(record, field):
                context[field] = getattr(record, field)

        payload: dict[str, object] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "event": context.pop("event", "log"),
            "message": record.getMessage(),
        }
        if context:
            payload["context"] = context
        return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def get_logger(component: str) -> logging.Logger:
    """Return a logger below the application's logging namespace."""

    return logging.getLogger(f"{LOGGER_NAME}.{component}")


def configure_logging(level: str, *, stream: TextIO | None = None) -> logging.Logger:
    """Configure one JSON stream handler and return the application logger."""

    normalized = normalize_log_level(level)
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(getattr(logging, normalized))
    logger.propagate = False

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

    output = sys.stderr if stream is None else stream
    handler = logging.StreamHandler(output)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    return logger


def context_from_mapping(values: Mapping[str, object]) -> dict[str, object]:
    """Keep only non-empty context fields for log records."""

    return {key: value for key, value in values.items() if value is not None}


__all__ = ["JsonFormatter", "configure_logging", "context_from_mapping", "get_logger"]
