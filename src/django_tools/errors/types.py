"""Error System - Basic Types.

Defines the fundamental error structure without internal dependencies.
This module is at the base of the import hierarchy.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ErrorItem(BaseModel):
    """Error item. Optional fields are not included if not provided."""

    message: str
    field: str | None = None
    code: int | None = None
    item: int | None = None  # optional index/identifier
    meta: dict[str, Any] = Field(default_factory=dict)
