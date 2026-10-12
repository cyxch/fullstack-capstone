"""Pydantic schemas for the versioned capstone item API."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import cast

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictInt,
    StrictStr,
    ValidationError,
    field_validator,
    model_validator,
)


def _validation_message(error: ValidationError) -> str:
    """Convert the first Pydantic issue into a short API-facing message."""

    detail = error.errors()[0]
    location = ".".join(str(part) for part in detail["loc"])
    message = str(detail["msg"])
    return f"{location}: {message}" if location else message


class ItemValidationError(ValueError):
    """Raised when an item cannot be created or updated."""

    code = "invalid_item"

    def as_dict(self) -> dict[str, str]:
        """Return a stable JSON-compatible error representation."""

        return {"code": self.code, "message": str(self)}


class ItemCreate(BaseModel):
    """Validated payload for creating a knowledge item."""

    model_config = ConfigDict(extra="forbid")

    title: StrictStr = Field(min_length=1, max_length=120)
    content: StrictStr = Field(default="", max_length=5000)

    @field_validator("title", "content")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        """Trim text while retaining meaningful internal whitespace."""

        return value.strip()

    @model_validator(mode="after")
    def require_title(self) -> ItemCreate:
        """Reject a title that becomes blank after whitespace normalization."""

        if not self.title:
            raise ValueError("item title cannot be empty")
        return self

    @classmethod
    def model_validate_payload(cls, payload: object) -> ItemCreate:
        """Validate arbitrary input and expose a domain-level error."""

        try:
            return cls.model_validate(payload)
        except ValidationError as exc:
            raise ItemValidationError(_validation_message(exc)) from exc


class ItemUpdate(BaseModel):
    """Validated partial payload for updating an item."""

    model_config = ConfigDict(extra="forbid")

    title: StrictStr | None = Field(default=None, min_length=1, max_length=120)
    content: StrictStr | None = Field(default=None, max_length=5000)

    @field_validator("title", "content")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        """Normalize supplied text and preserve omitted fields."""

        return value.strip() if value is not None else None

    @model_validator(mode="after")
    def require_one_field(self) -> ItemUpdate:
        """Reject an empty update body so PUT always has an explicit effect."""

        if self.title is None and self.content is None:
            raise ValueError("at least one item field is required")
        if self.title == "":
            raise ValueError("item title cannot be empty")
        return self


class Item(BaseModel):
    """Immutable item returned by the versioned API."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: StrictInt = Field(gt=0)
    title: StrictStr = Field(min_length=1, max_length=120)
    content: StrictStr = Field(max_length=5000)
    created_at: datetime
    updated_at: datetime

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        """Keep returned item titles non-blank."""

        normalized = value.strip()
        if not normalized:
            raise ValueError("item title cannot be empty")
        return normalized

    @field_validator("created_at", "updated_at")
    @classmethod
    def normalize_timestamp(cls, value: datetime) -> datetime:
        """Normalize naive timestamps to UTC for a stable response contract."""

        return (value.replace(tzinfo=UTC) if value.tzinfo is None else value).astimezone(UTC)

    @classmethod
    def new(cls, item_id: int, payload: ItemCreate) -> Item:
        """Build a new item with one shared creation/update timestamp."""

        now = datetime.now(UTC)
        return cls(
            id=item_id,
            title=payload.title,
            content=payload.content,
            created_at=now,
            updated_at=now,
        )

    def with_updates(self, payload: ItemUpdate) -> Item:
        """Return an updated immutable item while retaining its creation time."""

        return type(self)(
            id=self.id,
            title=self.title if payload.title is None else payload.title,
            content=self.content if payload.content is None else payload.content,
            created_at=self.created_at,
            updated_at=datetime.now(UTC),
        )

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-compatible representation for future persistence."""

        return cast(dict[str, object], self.model_dump(mode="json"))
