"""Error System - Reusable API Component.

Provides types, containers, and interfaces for standardized error handling
in REST APIs. Designed to be generic and reusable as a library component.

Architecture:
    - ErrorItem: Basic error structure
    - Errors: Error container with operations (normalize, normalize_codes, filter_by, merge)
    - to_errors(): Direct conversion function (alias for Errors.normalize)
    - ApiError: Generic base exception for APIs

Usage of API Interface (Errors):

    1. **Direct conversion** (classmethod):
        >>> errors = Errors.normalize("error")
        >>> errors = Errors.normalize(["error1", "error2"])
        >>> errors = Errors.normalize(ValidationError(...))

    2. **Incremental manipulation** (instance):
        >>> errors = Errors(root=[])
        >>> errors.add("error 1")
        >>> errors.add("error 2", field="email", code=400)
        >>> errors.add(ValidationError(...))

    3. **Shortcut function** (simplified interface):
        >>> errors = to_errors("error")
        >>> errors = to_errors(["error1", "error2"])
        >>> errors = to_errors(ValidationError(...))

    4. **Generic exception** (for raises):
        >>> raise ApiError("Business error")
        >>> raise ApiError({"message": "Error", "field": "email"}, code=400)

"""

from __future__ import annotations

from typing import Any

from .container import Errors
from .exceptions import ApiError
from .types import ErrorItem

__all__ = ["ApiError", "ErrorItem", "Errors", "to_errors"]


def to_errors(error: Any, code: int | None = None) -> Errors:
    """Converts any error type to Errors.

    Shortcut for Errors.normalize() - simplified public interface
    for direct conversion. For complex manipulation, use Errors directly.

    Args:
        error: Any error type (str, dict, list, Exception, Errors, etc.)
        code: Default error code (optional)

    Returns:
        Normalized Errors

    Examples:
        >>> to_errors("Simple error")
        >>> to_errors(ValidationError(...))
        >>> to_errors({"message": "error", "field": "name"}, code=400)
        >>> to_errors(["error1", "error2", "error3"])
        >>> to_errors([{"message": "error", "field": "name"}])

    """
    return Errors.normalize(error, code=code)
