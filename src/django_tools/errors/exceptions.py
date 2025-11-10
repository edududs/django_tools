"""Error System - Exceptions.

Defines API exceptions that carry structured error information.
"""

from __future__ import annotations

from typing import Any

from .container import Errors
from .types import ErrorItem


class ApiError(Exception):
    """API base exception that carries Errors internally.

    Represents standardized API/business errors that can be extended
    by domain-specific exceptions. Accepts any entry type
    and normalizes to Errors automatically.

    This class is generic and can be used in any API as a base
    for custom exceptions.

    Examples:
        >>> raise ApiError("Simple error")
        >>> raise ApiError({"message": "Error", "field": "email"}, code=400)
        >>> raise ApiError(ValidationError(...))

        # Custom domain extension:
        >>> class UserError(ApiError):
        ...     pass
        >>> raise UserError("Invalid user")

    """

    def __init__(
        self,
        error: str | ErrorItem | Errors | dict[str, Any] | Exception,
        code: int | None = None,
    ) -> None:
        """Initializes ApiError with any type of error.

        Args:
            error: String, ErrorItem, Errors, dict or Exception
            code: Default error code (optional)

        """
        super().__init__()
        # Uses Errors.normalize for normalization
        self._errors = Errors.normalize(error, code=code)

    @property
    def errors(self) -> Errors:
        """Returns the internal Errors."""
        return self._errors

    @property
    def message(self) -> str:
        """Returns the first message (for compatibility)."""
        messages = self._errors.messages
        if messages:
            return messages[0]
        # Return relative module name (e.g., "exceptions.ApiError")
        module = self.__class__.__module__.split(".")[-1]
        return f"{module}.{self.__class__.__name__}"

    def __str__(self) -> str:
        """String representation of the exception."""
        return self.message
