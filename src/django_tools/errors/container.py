# pyright: reportImportCycles=false

"""Error System - Container.

Defines the main Errors container with manipulation operations.
Combines types and normalization mixins.
"""

from __future__ import annotations

from typing import Any, Iterable, Iterator

from pydantic import RootModel

from .mixins import NormalizeErrorsMixin
from .types import ErrorItem


class Errors(NormalizeErrorsMixin, RootModel[list[ErrorItem]]):
    """Rich error container with manipulation operations.

    Represents a collection of ErrorItems with useful methods for
    adding, filtering, normalizing, and serializing errors.
    """

    root: list[ErrorItem]

    @property
    def errors(self) -> list[ErrorItem]:
        """Property referencing root for semantic compatibility."""
        return self.root

    def add(
        self,
        message: str | ErrorItem,
        *,
        field: str | None = None,
        code: int | None = None,
        item: int | None = None,
        **meta: Any,
    ) -> None:
        """Add an error to the bag."""
        if isinstance(message, ErrorItem):
            self.errors.append(message)
        else:
            self.errors.append(ErrorItem(message=message, field=field, code=code, item=item, meta=meta))

    def extend(self, items: Iterable[str | ErrorItem]) -> None:
        """Add multiple errors to the bag."""
        for it in items:
            self.add(it)

    def __bool__(self) -> bool:
        """Allows boolean checks."""
        return bool(self.errors)

    def __len__(self) -> int:
        """Number of errors in the bag."""
        return len(self.errors)

    def __iter__(self) -> Iterator[ErrorItem]:  # pyright: ignore[reportIncompatibleMethodOverride]
        """Allows iteration over errors in the bag."""
        yield from self.errors

    def __add__(self, other: Errors) -> Errors:
        """Add another Errors to this."""
        return Errors(root=self.errors + other.errors)

    def __sub__(self, other: Errors) -> Errors:
        """Remove errors present in 'other' from this Errors.

        Only exactly equal errors will be removed.
        """
        # ErrorItem is not hashable, so compare directly
        other_items = list(other.errors)
        result = [e for e in self.errors if e not in other_items]
        return Errors(root=result)

    @property
    def messages(self) -> list[str]:
        """Returns list of error messages."""
        return [e.message for e in self.errors]

    def normalize_codes(self, default_code: int) -> None:
        """Normalizes error codes, applying the default where none is defined.

        Args:
            default_code: Default code for errors without an explicit code

        """
        for error_item in self.errors:
            if error_item.code is None:
                error_item.code = default_code

    def filter_by(
        self,
        *,
        field: str | None = None,
        code: int | None = None,
        has_meta: bool | None = None,
    ) -> Errors:
        """Filter errors by specific criteria.

        Args:
            field: Filter by specific field
            code: Filter by specific code
            has_meta: Filter by presence of metadata

        Returns:
            New Errors with filtered errors

        """
        filtered = self.errors
        if field is not None:
            filtered = [e for e in filtered if e.field == field]
        if code is not None:
            filtered = [e for e in filtered if e.code == code]
        if has_meta is not None:
            filtered = [e for e in filtered if bool(e.meta) == has_meta]
        return Errors(root=filtered)

    def merge(self, other: Errors) -> None:
        """Merge another Errors into this one.

        Args:
            other: Errors to merge in

        """
        self.errors.extend(other.errors)

    def to_dict(self, exclude_unset: bool = True, exclude_none: bool = True) -> dict[str, Any]:
        """Serializes the bag removing undefined and None fields.

        Returns a format compatible with build_response which normalizes to
        {"description": [...], "data": [...]}.
        """
        items = [e.model_dump(exclude_unset=exclude_unset, exclude_none=exclude_none) for e in self.errors]
        messages = [i["message"] for i in items]
        return {"description": messages, "data": items}
