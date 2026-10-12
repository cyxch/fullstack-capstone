"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DATA_FILE = Path("data/tasks.json")
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_APP_NAME = "fullstack-capstone-backend"
DEFAULT_ENVIRONMENT = "development"
DEFAULT_CORS_ORIGINS = ("*",)
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
    """Runtime settings shared by the task CLI and HTTP application."""

    data_file: Path = DEFAULT_DATA_FILE
    log_level: str = DEFAULT_LOG_LEVEL
    app_name: str = DEFAULT_APP_NAME
    environment: str = DEFAULT_ENVIRONMENT
    cors_origins: tuple[str, ...] = DEFAULT_CORS_ORIGINS

    def __post_init__(self) -> None:
        if not isinstance(self.data_file, Path):
            raise ConfigError("data file must be a path")
        if not str(self.data_file).strip():
            raise ConfigError("data file cannot be empty")
        object.__setattr__(self, "log_level", normalize_log_level(self.log_level))
        if not isinstance(self.app_name, str) or not self.app_name.strip():
            raise ConfigError("app name cannot be empty")
        if not isinstance(self.environment, str) or not self.environment.strip():
            raise ConfigError("environment cannot be empty")
        origins = tuple(origin.strip() for origin in self.cors_origins if origin.strip())
        if not origins:
            raise ConfigError("at least one CORS origin is required")
        object.__setattr__(self, "app_name", self.app_name.strip())
        object.__setattr__(self, "environment", self.environment.strip())
        object.__setattr__(self, "cors_origins", origins)

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> Settings:
        """Build settings from ``TASK_*`` variables or their defaults."""

        source = os.environ if environ is None else environ
        raw_path = source.get("TASK_DATA_FILE", str(DEFAULT_DATA_FILE)).strip()
        if not raw_path:
            raise ConfigError("TASK_DATA_FILE cannot be empty")
        raw_level = source.get("TASK_LOG_LEVEL", DEFAULT_LOG_LEVEL)
        raw_origins = source.get("TASK_CORS_ORIGINS", ",".join(DEFAULT_CORS_ORIGINS))
        origins = tuple(origin.strip() for origin in raw_origins.split(","))
        return cls(
            data_file=Path(raw_path),
            log_level=raw_level,
            app_name=source.get("TASK_APP_NAME", DEFAULT_APP_NAME),
            environment=source.get("TASK_ENVIRONMENT", DEFAULT_ENVIRONMENT),
            cors_origins=origins,
        )

    def with_overrides(
        self,
        *,
        data_file: Path | None = None,
        log_level: str | None = None,
        app_name: str | None = None,
        environment: str | None = None,
        cors_origins: tuple[str, ...] | None = None,
    ) -> Settings:
        """Return a validated copy with command-line overrides applied."""

        return type(self)(
            data_file=self.data_file if data_file is None else data_file,
            log_level=self.log_level if log_level is None else log_level,
            app_name=self.app_name if app_name is None else app_name,
            environment=self.environment if environment is None else environment,
            cors_origins=self.cors_origins if cors_origins is None else cors_origins,
        )
