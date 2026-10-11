"""Pydantic input and persistence models for tasks."""

from __future__ import annotations

from typing import Literal, cast

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictInt,
    StrictStr,
    ValidationError,
    field_validator,
    model_validator,
)


def _validation_message(error: ValidationError) -> str:
    """Convert Pydantic's first validation issue into a concise domain message."""

    detail = error.errors()[0]
    location = ".".join(str(part) for part in detail["loc"])
    message = str(detail["msg"])
    return f"{location}: {message}" if location else message


class TaskValidationError(ValueError):
    """Raised when task input or persisted task data is invalid."""

    code = "invalid_task"

    def as_dict(self) -> dict[str, str]:
        """Return a stable, serializable error representation."""

        return {"code": self.code, "message": str(self)}


class TaskCreate(BaseModel):
    """Validated input for creating a task."""

    model_config = ConfigDict(extra="forbid")

    title: StrictStr = Field(min_length=1)

    @classmethod
    def model_validate_title(cls, title: str) -> TaskCreate:
        """Validate a title and translate Pydantic errors to a domain error."""

        try:
            normalized = title.strip()
        except (AttributeError, TypeError) as exc:
            raise TaskValidationError("task title must be a string") from exc
        if not normalized:
            raise TaskValidationError("task title cannot be empty")
        try:
            return cls(title=normalized)
        except ValidationError as exc:
            raise TaskValidationError(_validation_message(exc)) from exc


class TaskUpdate(BaseModel):
    """Validated fields for replacing a task through the HTTP API."""

    model_config = ConfigDict(extra="forbid")

    title: StrictStr | None = Field(default=None, min_length=1)
    completed: StrictBool | None = None

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str | None) -> str | None:
        """Normalize a supplied title while preserving omitted fields."""

        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("task title cannot be empty")
        return normalized

    @model_validator(mode="after")
    def require_one_field(self) -> TaskUpdate:
        """Reject an empty update body so PUT has an explicit effect."""

        if self.title is None and self.completed is None:
            raise ValueError("at least one task field is required")
        return self


class TaskQuery(BaseModel):
    """Validated filters accepted by the task list operation."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["all", "pending", "completed"] = "all"
    keyword: StrictStr | None = None

    @classmethod
    def model_validate_query(
        cls,
        *,
        status: str,
        keyword: str | None,
    ) -> TaskQuery:
        """Validate query values and expose domain-level errors."""

        try:
            normalized_keyword = keyword.strip() if keyword is not None else None
            allowed_status = cast(Literal["all", "pending", "completed"], status)
            return cls(status=allowed_status, keyword=normalized_keyword or None)
        except (ValidationError, AttributeError) as exc:
            if isinstance(exc, ValidationError):
                message = _validation_message(exc)
            else:
                message = "keyword must be a string"
            raise TaskValidationError(message) from exc


class Task(BaseModel):
    """Immutable task record persisted as JSON."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: StrictInt = Field(gt=0)
    title: StrictStr = Field(min_length=1)
    completed: StrictBool = False

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        """Keep persisted and newly created titles free of outer whitespace."""

        normalized = value.strip()
        if not normalized:
            raise ValueError("task title cannot be empty")
        return normalized

    @classmethod
    def model_validate_record(cls, payload: object) -> Task:
        """Validate an arbitrary JSON value as a task record."""

        if not isinstance(payload, dict):
            raise TaskValidationError("each task must be a JSON object")
        required = {"id", "title", "completed"}
        payload_keys = set(payload)
        if payload_keys != required:
            missing = ", ".join(sorted(required - payload_keys, key=str))
            extra = ", ".join(sorted(payload_keys - required, key=str))
            details = []
            if missing:
                details.append(f"missing fields: {missing}")
            if extra:
                details.append(f"unknown fields: {extra}")
            raise TaskValidationError("task fields are invalid (" + "; ".join(details) + ")")
        try:
            return cls.model_validate(payload)
        except ValidationError as exc:
            raise TaskValidationError(_validation_message(exc)) from exc

    @classmethod
    def from_dict(cls, payload: object) -> Task:
        """Backward-compatible name for validating a persisted record."""

        return cls.model_validate_record(payload)

    def to_dict(self) -> dict[str, object]:
        """Return the JSON-compatible representation of this task."""

        return cast(dict[str, object], self.model_dump(mode="json"))
