"""Error System - Normalization Mixins.

Provides conversion logic from various error types to Errors.
Uses TYPE_CHECKING to avoid circular imports with container.

Ninja/Django imports are lazy and optional to avoid forcing Django initialization.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, Sequence

from pydantic import ValidationError

from .types import ErrorItem

if TYPE_CHECKING:
    from ninja.errors import ValidationError as NinjaValidationError

    from .container import Errors


def _is_ninja_validation_error(obj: Any) -> bool:
    """Check if object is NinjaValidationError without importing it."""
    return type(obj).__name__ == "ValidationError" and type(obj).__module__ == "ninja.errors"


def _is_http_error(obj: Any) -> bool:
    """Check if object is HttpError without importing it."""
    return type(obj).__name__ == "HttpError" and type(obj).__module__ == "ninja.errors"


class NormalizeErrorsMixin:
    """Mixin to add error conversion methods to a class."""

    @classmethod
    def normalize(cls, error: Any, code: int | None = None) -> Errors:
        """Converts any error type to Errors (classmethod).

        Args:
            error: Any kind of error (Errors, ErrorItem, Exception, str, dict, etc.)
            code: Default error code (optional)

        Returns:
            Normalized Errors

        Examples:
            >>> Errors.normalize("simple error")
            >>> Errors.normalize(ValidationError(...))
            >>> Errors.normalize({"message": "error", "field": "name"})

        """
        from .container import Errors

        # Already Errors -> return as is
        if isinstance(error, Errors):
            return error

        # If ErrorItem -> wrap in Errors
        if isinstance(error, ErrorItem):
            return Errors(root=[error])

        # If ValidationError (pydantic or ninja) -> convert
        if isinstance(error, ValidationError) or _is_ninja_validation_error(error):
            return cls._from_validation_error(error)

        # If HttpError -> extract payload and normalize
        if _is_http_error(error):
            from .utils import extract_http_error_payload

            payload = extract_http_error_payload(error)
            return cls.normalize(payload, code=code)

        # If ApiError -> return exc.errors
        # Check by class name to avoid forward reference
        if isinstance(error, Exception) and hasattr(error, "errors") and type(error).__name__ == "ApiError":
            return error.errors  # type: ignore[attr-defined]

        # If dict/mapping -> convert
        if isinstance(error, Mapping):
            return cls._from_dict(error, code=code)

        # If sequence (except str) -> convert
        if isinstance(error, Sequence) and not isinstance(error, str):
            return cls._from_sequence(error, code=code)

        # If generic Exception -> convert
        if isinstance(error, Exception):
            return Errors(root=[ErrorItem(message=str(error), code=code)])

        # Fallback: convert to string
        return Errors(root=[ErrorItem(message=str(error), code=code)])

    @classmethod
    def _from_validation_error(cls, exc: ValidationError | NinjaValidationError) -> Errors:
        """Converts Pydantic or Ninja ValidationError to Errors.

        Args:
            exc: ValidationError from Pydantic or Ninja (duck typed)

        """
        from .container import Errors

        # Extract errors list (both ValidationError types have .errors())
        if hasattr(exc, "errors") and callable(exc.errors):
            errors_result = exc.errors()
            errors = list[Any](errors_result) if errors_result else []
        else:
            errors = []

        if not errors:
            return Errors(root=[ErrorItem(message=str(exc))])

        error_items = [
            ErrorItem(
                message=err.get("msg", "Validation error"),
                field=".".join(str(loc) for loc in err.get("loc", [])) or None,
                meta={"type": err.get("type", "validation_error"), "input": err.get("input")},
            )
            for err in errors
            if err.get("msg")  # Filter out errors without messages
        ]

        return Errors(root=error_items)

    @classmethod
    def _from_dict(cls, error: Mapping[str, Any], code: int | None = None) -> Errors:
        """Converts error dict to Errors."""
        # Case 1: complete Errors format (description + data)
        if "data" in error:
            return cls._from_error_bag_format(error, code)

        # Case 2: dict with description (list or string)
        if "description" in error:
            return cls._from_description_format(error, code)

        # Case 3: generic dict with ErrorItem fields
        return cls._from_generic_dict(error, code)

    @classmethod
    def _from_error_bag_format(cls, error: Mapping[str, Any], code: int | None) -> Errors:
        """Converts dict in Errors format (with data)."""
        from .container import Errors

        error_items = [
            ErrorItem(**item) if isinstance(item, dict) else ErrorItem(message=str(item), code=code)
            for item in error.get("data", [])
        ]
        return Errors(root=error_items)

    @classmethod
    def _from_description_format(cls, error: Mapping[str, Any], code: int | None) -> Errors:
        """Converts dict with description (list or string)."""
        from .container import Errors

        description = error["description"]
        if isinstance(description, list):
            error_items = [ErrorItem(message=msg, code=code) for msg in description if msg]
        else:
            error_items = [ErrorItem(message=str(description), code=code)]
        return Errors(root=error_items)

    @classmethod
    def _from_generic_dict(cls, error: Mapping[str, Any], code: int | None) -> Errors:
        """Converts generic dict to ErrorItem.

        Explicit values from the dict are used, with code as fallback.
        """
        from .container import Errors

        message = error.get("message") or error.get("msg") or str(error)
        field = error.get("field")
        # Use explicit code from dict, even if 0 or None
        error_code = error.get("code") if "code" in error else code
        item = error.get("item") if "item" in error else None

        # If explicit "meta" key, use directly; else collect extra fields as metadata
        if "meta" in error:
            meta = error["meta"] if isinstance(error["meta"], dict) else {}
        else:
            meta = {
                k: v for k, v in error.items() if k not in {"message", "msg", "field", "code", "item", "meta"}
            }

        return Errors(root=[ErrorItem(message=message, field=field, code=error_code, item=item, meta=meta)])

    @classmethod
    def _from_sequence(cls, error: Sequence[Any], code: int | None = None) -> Errors:
        """Converts a sequence (list/tuple/set) of errors to Errors.

        Supports heterogeneous lists with any type:
        - ErrorItem: added directly
        - Errors: extract and add internal items
        - ApiError: extract internal errors
        - ValidationError (Pydantic/Ninja): structed conversion
        - HttpError: extract payload and process recursively
        - dict: convert to ErrorItem
        - Exception: convert to ErrorItem
        - str: convert to ErrorItem
        - Any other: str(item) → ErrorItem

        Examples:
            >>> Errors.normalize(["error1", "error2"])
            >>> Errors.normalize([{"message": "error", "field": "name"}, "simple error"])
            >>> Errors.normalize([ValidationError(...), "another error"])
            >>> Errors.normalize([1, ValueError("error"), "text", 255])

        """
        from .container import Errors

        error_items = []
        for item in error:
            if isinstance(item, ErrorItem):
                # Direct ErrorItem
                error_items.append(item)
            elif isinstance(item, Errors):
                # Errors -> extract internal items
                error_items.extend(item.errors)
            elif isinstance(item, ValidationError) or _is_ninja_validation_error(item):
                # ValidationError -> smart structured conversion
                error_items.extend(cls._from_validation_error(item).errors)
            elif _is_http_error(item):
                # HttpError -> extract payload and process recursively
                from .utils import extract_http_error_payload

                payload = extract_http_error_payload(item)
                error_items.extend(cls.normalize(payload, code=code).errors)
            elif (
                isinstance(item, Exception) and hasattr(item, "errors") and type(item).__name__ == "ApiError"
            ):
                # ApiError -> extract internal errors
                # Check by class name to avoid forward reference
                error_items.extend(item.errors.errors)  # type: ignore[attr-defined]
            elif isinstance(item, dict):
                # Dict -> convert recursively
                error_items.extend(cls._from_dict(item, code=code).errors)
            elif isinstance(item, Exception):
                # Generic Exception -> convert to ErrorItem
                error_items.append(ErrorItem(message=str(item), code=code))
            else:
                # Any other type -> str(item)
                error_items.append(ErrorItem(message=str(item), code=code))
        return Errors(root=error_items)
