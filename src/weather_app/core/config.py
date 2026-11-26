"""Centralized application and weather API configuration.

Author: Akash Das
"""

from dataclasses import dataclass
import os


WEATHER_PROVIDER: str = "open-meteo"
FORECAST_API_BASE_URL: str = "https://api.open-meteo.com/v1/forecast"
GEOCODING_API_BASE_URL: str = "https://geocoding-api.open-meteo.com/v1/search"

DEFAULT_TIMEZONE: str = "auto"
DEFAULT_FORECAST_DAYS: int = 7
DEFAULT_REQUEST_TIMEOUT_SECONDS: int = 10

DEFAULT_TEMPERATURE_UNIT: str = "celsius"
DEFAULT_WIND_SPEED_UNIT: str = "kmh"
DEFAULT_PRECIPITATION_UNIT: str = "mm"

DEFAULT_GEOCODING_COUNT: int = 5
DEFAULT_GEOCODING_LANGUAGE: str = "en"

CURRENT_VARIABLES: tuple[str, ...] = (
    "temperature_2m",
    "relative_humidity_2m",
    "apparent_temperature",
    "precipitation",
    "rain",
    "wind_speed_10m",
    "wind_direction_10m",
    "weather_code",
)

HOURLY_VARIABLES: tuple[str, ...] = (
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation_probability",
    "precipitation",
    "wind_speed_10m",
    "wind_direction_10m",
    "weather_code",
)

DAILY_VARIABLES: tuple[str, ...] = (
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "precipitation_probability_max",
    "wind_speed_10m_max",
    "weather_code",
    "sunrise",
    "sunset",
)


@dataclass(frozen=True)
class APIConfig:
    """Immutable configuration for the weather and geocoding API clients."""

    provider: str = WEATHER_PROVIDER
    forecast_base_url: str = FORECAST_API_BASE_URL
    geocoding_base_url: str = GEOCODING_API_BASE_URL
    timeout_seconds: int = DEFAULT_REQUEST_TIMEOUT_SECONDS
    timezone: str = DEFAULT_TIMEZONE
    forecast_days: int = DEFAULT_FORECAST_DAYS
    temperature_unit: str = DEFAULT_TEMPERATURE_UNIT
    wind_speed_unit: str = DEFAULT_WIND_SPEED_UNIT
    precipitation_unit: str = DEFAULT_PRECIPITATION_UNIT
    geocoding_count: int = DEFAULT_GEOCODING_COUNT
    geocoding_language: str = DEFAULT_GEOCODING_LANGUAGE
    current_variables: tuple[str, ...] = CURRENT_VARIABLES
    hourly_variables: tuple[str, ...] = HOURLY_VARIABLES
    daily_variables: tuple[str, ...] = DAILY_VARIABLES


def get_api_config() -> APIConfig:
    """Build an APIConfig instance with optional environment variable overrides."""
    return APIConfig(
        provider=os.getenv("WEATHER_PROVIDER", WEATHER_PROVIDER),
        timezone=os.getenv("DEFAULT_TIMEZONE", DEFAULT_TIMEZONE),
        forecast_days=int(os.getenv("FORECAST_DAYS", str(DEFAULT_FORECAST_DAYS))),
        temperature_unit=os.getenv("TEMPERATURE_UNIT", DEFAULT_TEMPERATURE_UNIT),
        wind_speed_unit=os.getenv("WIND_SPEED_UNIT", DEFAULT_WIND_SPEED_UNIT),
        precipitation_unit=os.getenv("PRECIPITATION_UNIT", DEFAULT_PRECIPITATION_UNIT),
    )
