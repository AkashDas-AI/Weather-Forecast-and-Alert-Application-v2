"""Weather API client interface (Phase 3 preparation; HTTP fetching in Phase 4).

Author: Akash Das
"""

from typing import Any

from weather_app.core.config import APIConfig, get_api_config


class WeatherAPIClient:
    """Interface for retrieving forecast data from the configured weather provider.

    Phase 4 will implement HTTP communication, request timeouts, connection error
    handling, and HTTP status-code validation.
    """

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
            "forecast_days": forecast_days or self.config.forecast_days,
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
        """Fetch raw forecast JSON for the given coordinates (implemented in Phase 4)."""
        raise NotImplementedError(
            "Live weather API HTTP fetching will be implemented in Phase 4."
        )
