"""In-memory storage used by the Week 7 item API."""

from __future__ import annotations

from collections.abc import Sequence

from .item_models import Item


class InMemoryItemStorage:
    """Small isolated storage adapter for local development and tests."""

    def __init__(self, items: Sequence[Item] | None = None) -> None:
        self._items = list(items or [])

    def load(self) -> list[Item]:
        """Return a copy so callers cannot mutate storage accidentally."""

        return list(self._items)

    def save(self, items: Sequence[Item]) -> None:
        """Replace the in-memory snapshot with a copied sequence."""

        self._items = list(items)
