"""
Backend-side validation helpers (Step 5).

Never trust frontend validation alone — every field a user controls is
re-checked here before it touches the database. Validators raise
ValidationError, which the centralized error handler (app/utils/errors.py)
converts into a consistent 422 JSON response.
"""

import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ValidationError(Exception):
    """Carries a dict of field -> list[str] messages. Raised by services, caught by routes/errors.py."""

    def __init__(self, errors: dict):
        self.errors = errors
        super().__init__("Validation failed")


class NotFoundError(Exception):
    """Raised by services when a looked-up entity (by slug/id/reference_code) doesn't exist."""

    def __init__(self, message: str = "The requested resource was not found."):
        self.message = message
        super().__init__(message)


class Validator:
    """Accumulates field errors across multiple checks, then raises once via .finish()."""

    def __init__(self):
        self._errors: dict[str, list[str]] = {}

    def _add(self, field: str, message: str):
        self._errors.setdefault(field, []).append(message)

    def require(self, data: dict, field: str, label: str | None = None) -> "Validator":
        label = label or field
        value = data.get(field)
        if value is None or (isinstance(value, str) and value.strip() == ""):
            self._add(field, f"{label} is required.")
        return self

    def max_length(self, data: dict, field: str, max_len: int, label: str | None = None) -> "Validator":
        label = label or field
        value = data.get(field)
        if isinstance(value, str) and len(value) > max_len:
            self._add(field, f"{label} must be {max_len} characters or fewer.")
        return self

    def email(self, data: dict, field: str, label: str | None = None) -> "Validator":
        label = label or field
        value = data.get(field)
        if value and not EMAIL_RE.match(str(value)):
            self._add(field, f"{label} must be a valid email address.")
        return self

    def one_of(self, data: dict, field: str, allowed: set, label: str | None = None) -> "Validator":
        label = label or field
        value = data.get(field)
        if value is not None and value not in allowed:
            self._add(field, f"{label} must be one of: {', '.join(sorted(allowed))}.")
        return self

    def is_bool(self, data: dict, field: str, label: str | None = None) -> "Validator":
        label = label or field
        value = data.get(field)
        if value is not None and not isinstance(value, bool):
            self._add(field, f"{label} must be true or false.")
        return self

    def is_int(self, data: dict, field: str, label: str | None = None) -> "Validator":
        label = label or field
        value = data.get(field)
        if value is not None and not isinstance(value, int):
            self._add(field, f"{label} must be a whole number.")
        return self

    def finish(self):
        if self._errors:
            raise ValidationError(self._errors)
