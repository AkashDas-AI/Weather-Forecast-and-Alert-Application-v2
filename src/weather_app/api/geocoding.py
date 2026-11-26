"""Geocoding client interface (Phase 3 preparation; HTTP search in Phase 4).

Author: Akash Das
"""

from typing import Any

from weather_app.core.config import APIConfig, get_api_config


class GeocodingClient:
    """Interface for resolving location names to geographic coordinates.

    Phase 4 will implement HTTP requests to the Open-Meteo Geocoding API,
    candidate result handling for ambiguous city names, and error handling.
    """

    def __init__(self, config: APIConfig | None = None) -> None:
        """Initialize the geocoding client with centralized API configuration."""
        self.config = config or get_api_config()

    def build_search_params(
        self,
        query: str,
        count: int | None = None,
        language: str | None = None,
    ) -> dict[str, Any]:
        """Construct Open-Meteo geocoding query parameters from configuration."""
        return {
            "name": query,
            "count": count or self.config.geocoding_count,
            "language": language or self.config.geocoding_language,
            "format": "json",
        }

    def search_location(
        self,
        query: str,
        count: int | None = None,
        language: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search matching locations for a query string (implemented in Phase 4)."""
        raise NotImplementedError(
            "Live geocoding HTTP requests will be implemented in Phase 4."
        )
