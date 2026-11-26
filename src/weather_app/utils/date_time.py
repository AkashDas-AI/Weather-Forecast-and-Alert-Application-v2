"""Date and time parsing helper utilities.

Author: Akash Das
"""

from datetime import date, datetime
from typing import Any

from weather_app.core.exceptions import DataParsingError


def parse_iso_datetime(value: Any, field_name: str) -> datetime:
    """Parse an ISO-8601 datetime string into a Python datetime object."""
    if not isinstance(value, str) or not value.strip():
        raise DataParsingError(f"Field '{field_name}' must be a non-empty ISO datetime string.")
    try:
        return datetime.fromisoformat(value.strip())
    except ValueError as exc:
        raise DataParsingError(
            f"Field '{field_name}' has invalid ISO datetime format."
        ) from exc


def parse_iso_date(value: Any, field_name: str) -> date:
    """Parse an ISO-8601 date string into a Python date object."""
    if not isinstance(value, str) or not value.strip():
        raise DataParsingError(f"Field '{field_name}' must be a non-empty ISO date string.")
    try:
        return date.fromisoformat(value.strip())
    except ValueError as exc:
        raise DataParsingError(
            f"Field '{field_name}' has invalid ISO date format."
        ) from exc
