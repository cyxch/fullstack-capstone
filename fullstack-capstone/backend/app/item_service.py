"""Business rules for the versioned capstone item API."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from .item_models import Item, ItemCreate, ItemUpdate


class ItemStore(Protocol):
    """Minimal storage contract used by the item service."""

    def load(self) -> list[Item]:
        """Return the current item snapshot."""

    def save(self, items: Sequence[Item]) -> None:
        """Replace the current item snapshot."""


class ItemError(Exception):
    """Base class for expected item API failures."""

    code = "item_error"


class ItemNotFoundError(ItemError):
    """Raised when an item id does not exist."""

    code = "item_not_found"


class DuplicateItemTitleError(ItemError):
    """Raised when an item title is already in use."""

    code = "duplicate_item_title"


class ItemService:
    """Apply item rules while delegating storage to an adapter."""

    def __init__(self, storage: ItemStore) -> None:
        self.storage = storage

    def list_items(self) -> list[Item]:
        """Return items in insertion order."""

        return self.storage.load()

    def get_item(self, item_id: int) -> Item:
        """Return one item or raise a stable not-found error."""

        for item in self.storage.load():
            if item.id == item_id:
                return item
        raise ItemNotFoundError(f"item not found: {item_id}")

    def create_item(self, payload: ItemCreate) -> Item:
        """Validate uniqueness, allocate an id, and store a new item."""

        items = self.storage.load()
        if any(item.title.casefold() == payload.title.casefold() for item in items):
            raise DuplicateItemTitleError(f"item title already exists: {payload.title}")
        item = Item.new(max((candidate.id for candidate in items), default=0) + 1, payload)
        self.storage.save([*items, item])
        return item

    def update_item(self, item_id: int, payload: ItemUpdate) -> Item:
        """Apply a partial update while enforcing title uniqueness."""

        items = self.storage.load()
        for index, item in enumerate(items):
            if item.id != item_id:
                continue
            updated = item.with_updates(payload)
            if any(
                candidate.id != item_id and candidate.title.casefold() == updated.title.casefold()
                for candidate in items
            ):
                raise DuplicateItemTitleError(f"item title already exists: {updated.title}")
            items[index] = updated
            self.storage.save(items)
            return updated
        raise ItemNotFoundError(f"item not found: {item_id}")

    def delete_item(self, item_id: int) -> None:
        """Delete an item or raise a stable not-found error."""

        items = self.storage.load()
        for index, item in enumerate(items):
            if item.id == item_id:
                items.pop(index)
                self.storage.save(items)
                return
        raise ItemNotFoundError(f"item not found: {item_id}")
