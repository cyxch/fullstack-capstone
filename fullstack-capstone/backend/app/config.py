"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DATA_FILE = Path("data/tasks.json")
DEFAULT_LOG_LEVEL = "INFO"
LOG_LEVELS = frozenset({"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"})


class ConfigError(ValueError):
    """Raised when application configuration is invalid."""

    code = "invalid_configuration"

    def as_dict(self) -> dict[str, str]:
        """Return a stable, serializable error representation."""

        return {"code": self.code, "message": str(self)}


def normalize_log_level(value: str) -> str:
    """Normalize and validate a logging level."""

    if not isinstance(value, str):
        raise ConfigError("log level must be a string")
    normalized = value.strip().upper()
    if normalized not in LOG_LEVELS:
        allowed = ", ".join(sorted(LOG_LEVELS))
        raise ConfigError(f"unsupported log level {value!r}; choose one of {allowed}")
    return normalized


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime settings for the task CLI and service layer."""

    data_file: Path = DEFAULT_DATA_FILE
    log_level: str = DEFAULT_LOG_LEVEL

    def __post_init__(self) -> None:
        if not isinstance(self.data_file, Path):
            raise ConfigError("data file must be a path")
        if not str(self.data_file).strip():
            raise ConfigError("data file cannot be empty")
        object.__setattr__(self, "log_level", normalize_log_level(self.log_level))

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> Settings:
        """Build settings from ``TASK_*`` variables or their defaults."""

        source = os.environ if environ is None else environ
        raw_path = source.get("TASK_DATA_FILE", str(DEFAULT_DATA_FILE)).strip()
        if not raw_path:
            raise ConfigError("TASK_DATA_FILE cannot be empty")
        raw_level = source.get("TASK_LOG_LEVEL", DEFAULT_LOG_LEVEL)
        return cls(data_file=Path(raw_path), log_level=raw_level)

    def with_overrides(
        self,
        *,
        data_file: Path | None = None,
        log_level: str | None = None,
    ) -> Settings:
        """Return a validated copy with command-line overrides applied."""

        return type(self)(
            data_file=self.data_file if data_file is None else data_file,
            log_level=self.log_level if log_level is None else log_level,
        )
