"""Weather API client for fetching Open-Meteo forecast data.

Author: Akash Das
"""

from typing import Any

from weather_app.api._http import perform_get_json
from weather_app.core.config import APIConfig, get_api_config


def _is_valid_number(value: Any) -> bool:
    """Return True if value is an int or float (excluding bool)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


class WeatherAPIClient:
    """Client for retrieving raw forecast JSON from the configured weather provider."""

    def __init__(self, config: APIConfig | None = None) -> None:
        """Initialize the client with centralized API configuration."""
        self.config = config or get_api_config()

    def build_forecast_params(
        self,
        latitude: float,
        longitude: float,
        forecast_days: int | None = None,
        timezone: str | None = None,
    ) -> dict[str, Any]:
        """Construct Open-Meteo forecast query parameters from configuration."""
        return {
            "latitude": latitude,
            "longitude": longitude,
            "current": ",".join(self.config.current_variables),
            "hourly": ",".join(self.config.hourly_variables),
            "daily": ",".join(self.config.daily_variables),
            "timezone": timezone or self.config.timezone,
            "forecast_days": forecast_days if forecast_days is not None else self.config.forecast_days,
            "temperature_unit": self.config.temperature_unit,
            "wind_speed_unit": self.config.wind_speed_unit,
            "precipitation_unit": self.config.precipitation_unit,
        }

    def fetch_forecast(
        self,
        latitude: float,
        longitude: float,
        forecast_days: int | None = None,
        timezone: str | None = None,
    ) -> dict[str, Any]:
        """Fetch raw forecast JSON dictionary for the given WGS84 coordinates."""
        if not _is_valid_number(latitude) or not (-90.0 <= float(latitude) <= 90.0):
            raise ValueError("Latitude must be a number between -90 and 90.")
        if not _is_valid_number(longitude) or not (-180.0 <= float(longitude) <= 180.0):
            raise ValueError("Longitude must be a number between -180 and 180.")
        if forecast_days is not None and (
            isinstance(forecast_days, bool)
            or not isinstance(forecast_days, int)
            or not (1 <= forecast_days <= 16)
        ):
            raise ValueError("forecast_days must be an integer between 1 and 16.")

        params = self.build_forecast_params(
            latitude=float(latitude),
            longitude=float(longitude),
            forecast_days=forecast_days,
            timezone=timezone,
        )
        return perform_get_json(
            url=self.config.forecast_base_url,
            params=params,
            timeout=self.config.timeout_seconds,
        )
