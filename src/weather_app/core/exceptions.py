"""Custom application exception classes.

Author: Akash Das
"""


class WeatherAppError(Exception):
    """Base exception for the Weather Forecast & Alert Application."""


class ConfigurationError(WeatherAppError):
    """Raised when application or API configuration is invalid."""


class APIError(WeatherAppError):
    """Base exception for weather and geocoding API communication failures."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class APITimeoutError(APIError):
    """Raised when an API request exceeds the configured timeout."""


class APIConnectionError(APIError):
    """Raised when a network or connection error occurs during an API call."""


class GeocodingError(APIError):
    """Raised when location search or coordinate resolution fails."""


class LocationNotFoundError(GeocodingError):
    """Raised when geocoding returns no matching locations for a query."""


class DataParsingError(WeatherAppError):
    """Raised when API JSON data is missing required fields or has invalid types."""
