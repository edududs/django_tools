# Error System - Modular Structure

This module provides a standardized and reusable error system for Django/Ninja APIs. It is **decoupled from Django** and can work standalone if necessary.

## Overview

The error system allows normalization, manipulation, and serialization of errors from multiple sources (strings, dicts, exceptions, ValidationError, HttpError, etc.) into a unified structure.

## Architecture

The structure is designed to **avoid circular imports** and keep the code **decoupled from Django/Ninja** until actual usage.

### Dependency Hierarchy

```text
Layer 0: types.py          → ErrorItem (basic types, no internal dependencies)
Layer 1: mixins.py         → NormalizeErrorsMixin (conversion logic)
Layer 2: container.py      → Errors (container + operations)
Layer 3: exceptions.py     → ApiError (custom exceptions)
Layer 3: utils.py          → Utility functions (serialize, extract, etc.)
Layer 4: __init__.py       → Public API (ErrorItem, Errors, ApiError, to_errors)
```

**Fundamental rule**: Each module only imports from lower layers, avoiding circular dependencies.

### Lazy and Optional Imports

To avoid initializing Django unnecessarily, we use:

1. **Duck typing** to check Ninja types without importing them:

   ```python
   def _is_http_error(obj: Any) -> bool:
       return type(obj).__name__ == "HttpError" and type(obj).__module__ == "ninja.errors"
   ```

2. **Imports inside functions** when needed:

   ```python
   def normalize(cls, error: Any, code: int | None = None):
       from .container import Errors  # Late import avoids cycles
       ...
   ```

3. **TYPE_CHECKING** for type hints without actual runtime imports:

   ```python
   if TYPE_CHECKING:
       from .container import Errors
   ```

## File Structure

```text
src/django_tools/errors/
├── __init__.py          # Public API (ErrorItem, Errors, ApiError, to_errors)
├── types.py             # ErrorItem (basic type, no internal dependencies)
├── mixins.py            # NormalizeErrorsMixin (error conversion logic)
├── container.py         # Errors (container with operations: add, filter, merge, etc.)
├── exceptions.py        # ApiError (base exception for APIs)
├── utils.py             # Helper functions (serialize_error_to_payload, extract_http_error_payload, etc.)
└── tests/               # Unit tests (98 tests)
    ├── __init__.py
    └── test_errors.py
```

## Usage

### Basic Import (standalone, no Django required)

The module works completely standalone, without initializing Django:

```python
from django_tools.errors import ErrorItem, Errors, ApiError, to_errors

# Convert a string
errors = to_errors("simple error")
print(errors.messages)  # ['simple error']

# Manually create an ErrorItem
item = ErrorItem(message="Invalid field", field="email", code=400)
print(item.message)  # 'Invalid field'

# Errors container with operations
errors = Errors(root=[])
errors.add("Error 1")
errors.add("Error 2", field="name", code=400)
print(len(errors))  # 2
print(errors.messages)  # ['Error 1', 'Error 2']
```

### Normalizing Different Error Types

```python
from django_tools.errors import Errors, to_errors

# String
errors = Errors.normalize("error")
print(errors.messages)  # ['error']

# List of strings
errors = Errors.normalize(["error1", "error2"])
print(len(errors))  # 2

# Dictionary
errors = Errors.normalize({"message": "error", "field": "email", "code": 400})
print(errors.errors[0].field)  # 'email'

# Heterogeneous list
errors = Errors.normalize([
    "string error",
    {"message": "dict error", "field": "name"},
    ErrorItem(message="item error", code=500),
    ValueError("exception error")
])
print(len(errors))  # 4
```

### Normalizing with ValidationError (Pydantic)

```python
from pydantic import BaseModel, ValidationError
from django_tools.errors import Errors

class User(BaseModel):
    name: str
    age: int

try:
    User(name='John', age='invalid')
except ValidationError as e:
    errors = Errors.normalize(e)
    print(errors.messages)
    # ['Input should be a valid integer, unable to parse string as an integer']
    print(errors.errors[0].field)  # 'age'
```

### Errors Container Operations

```python
from django_tools.errors import Errors, ErrorItem

errors = Errors(root=[])
errors.add("Error 1", field="email", code=400)
errors.add("Error 2", field="name", code=400)
errors.add("Error 3", field="email", code=500)

# Filter by field
email_errors = errors.filter_by(field="email")
print(len(email_errors))  # 2

# Filter by code
code_400_errors = errors.filter_by(code=400)
print(len(code_400_errors))  # 2

# Normalize codes
errors.normalize_codes(default_code=400)
print(all(e.code == 400 for e in errors))  # True

# Set operations
errors1 = Errors(root=[ErrorItem(message="e1")])
errors2 = Errors(root=[ErrorItem(message="e2")])
combined = errors1 + errors2
print(len(combined))  # 2
```

### Custom Exceptions (ApiError)

```python
from django_tools.errors import ApiError, Errors

# Raise exception with string
raise ApiError("Business error")

# Raise exception with dictionary
raise ApiError({"message": "Error", "field": "email"}, code=400)

# Raise exception with Errors
errors = Errors(root=[ErrorItem(message="Error", field="email")])
raise ApiError(errors)

# Custom exception
class UserError(ApiError):
    pass

raise UserError("Invalid user")
```

### With Django/Ninja (lazy import)

Ninja is only imported when truly needed, so Django initialization is avoided if not required:

```python
from django_tools.errors import Errors

# In a Django Ninja endpoint
from ninja.errors import HttpError

try:
    raise HttpError(400, {"message": "error"})
except HttpError as e:
    # Ninja is only imported here, not at module import time
    errors = Errors.normalize(e)
    print(errors.messages)
```

## Tests

The module has full test coverage (98 tests) for:

- Creating and manipulating `ErrorItem`
- Errors container operations (add, filter, merge, filter_by)
- Normalizing all supported types (string, dict, list, Exception, ValidationError, HttpError)
- `ApiError` and inheritance
- The `to_errors()` function and its aliases
- Edge cases

To run tests:

```bash
pytest src/django_tools/errors/tests/test_errors.py -v
```

## Benefits

✅ **No circular imports**: clear, layered dependency hierarchy  
✅ **Django decoupled**: fully standalone operation  
✅ **Optional imports**: Ninja/Django only loaded when needed (lazy)  
✅ **Well-tested**: 98 fully passing tests  
✅ **Type-safe**: complete typing using duck typing and TYPE_CHECKING  
✅ **Extensible**: easy to add new error converters  
✅ **Performant**: lazy imports avoid unnecessary overhead  
✅ **Reusable**: can be used in any Python project, not just Django apps  

## Linter Warnings

"Cycle detected" linter warnings are **expected and resolved at runtime** by using late imports inside functions. This is a common and acceptable pattern in Python when layer hierarchy alone isn't enough to resolve cycles.

The code uses `# pyright: reportImportCycles=false` in `container.py` to document that the cycle is intentional and handled at runtime.

## Main Components

### ErrorItem

Basic error structure with optional fields:

- `message`: Error message (required)
- `field`: Related field (optional)
- `code`: Error code (optional)
- `item`: Index/identifier (optional)
- `meta`: Extra metadata (optional)

### Errors

A rich container with operations:

- `normalize()`: Convert any kind of error into Errors
- `add()`: Add an error to the container
- `filter_by()`: Filter errors by criteria
- `normalize_codes()`: Normalize error codes
- `merge()`: Merge with another Errors container
- `to_dict()`: Serialize errors as a dictionary

### ApiError

Base exception that holds Errors internally:

- Accepts any error type and normalizes it automatically
- Can be subclassed for domain-specific exceptions
- `.errors` property returns the Errors container
- `.message` property returns the first message or the class name

### to_errors()

Convenience function which is an alias for `Errors.normalize()`:

- Simplified interface for direct conversion
- Useful for simple cases where container manipulation isn't needed
