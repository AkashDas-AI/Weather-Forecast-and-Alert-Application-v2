"""Geocoding client for resolving location names via Open-Meteo Geocoding API.

Author: Akash Das
"""

from typing import Any

from weather_app.api._http import perform_get_json
from weather_app.core.config import APIConfig, get_api_config
from weather_app.core.exceptions import APIError, LocationNotFoundError


class GeocodingClient:
    """Client for resolving location search strings to geographic coordinates."""

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
            "count": count if count is not None else self.config.geocoding_count,
            "language": language or self.config.geocoding_language,
            "format": "json",
        }

    def search_location(
        self,
        query: str,
        count: int | None = None,
        language: str | None = None,
    ) -> dict[str, Any]:
        """Search matching locations for a query string and return raw JSON dict.

        Raises ValueError for invalid inputs and LocationNotFoundError when the API
        returns no matching results.
        """
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Location search query must be a non-empty string.")
        if count is not None and (
            isinstance(count, bool)
            or not isinstance(count, int)
            or not (1 <= count <= 100)
        ):
            raise ValueError("count must be an integer between 1 and 100.")

        cleaned_query = query.strip()
        params = self.build_search_params(
            query=cleaned_query,
            count=count,
            language=language,
        )
        payload = perform_get_json(
            url=self.config.geocoding_base_url,
            params=params,
            timeout=self.config.timeout_seconds,
        )

        if "results" not in payload:
            raise LocationNotFoundError(
                f"No locations found matching '{cleaned_query}'."
            )

        results = payload["results"]
        if not isinstance(results, list):
            raise APIError(
                "Malformed geocoding response: expected 'results' to be a list."
            )
        if len(results) == 0:
            raise LocationNotFoundError(
                f"No locations found matching '{cleaned_query}'."
            )

        return payload
