"""Structured weather and location data models.

Author: Akash Das
"""

from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class LocationInfo:
    """Structured representation of a geocoded location."""

    name: str
    latitude: float
    longitude: float
    timezone: str | None = None
    country: str | None = None
    country_code: str | None = None
    admin1: str | None = None
    elevation: float | None = None
    population: int | None = None
    location_id: int | None = None


@dataclass(frozen=True)
class ForecastMetadata:
    """Geographic coordinates and timezone metadata for a forecast response."""

    latitude: float
    longitude: float
    timezone: str
    timezone_abbreviation: str | None = None
    elevation: float | None = None
    utc_offset_seconds: int | None = None


@dataclass(frozen=True)
class CurrentWeather:
    """Current weather observation record."""

    time: datetime
    temperature_2m: float
    relative_humidity_2m: float | None = None
    apparent_temperature: float | None = None
    precipitation: float | None = None
    rain: float | None = None
    wind_speed_10m: float | None = None
    wind_direction_10m: float | None = None
    weather_code: int | None = None


@dataclass(frozen=True)
class HourlyForecast:
    """Single hourly forecast record."""

    time: datetime
    temperature_2m: float
    relative_humidity_2m: float | None = None
    precipitation_probability: float | None = None
    precipitation: float | None = None
    wind_speed_10m: float | None = None
    wind_direction_10m: float | None = None
    weather_code: int | None = None


@dataclass(frozen=True)
class DailyForecast:
    """Single daily forecast record."""

    date: date
    temperature_2m_max: float
    temperature_2m_min: float
    precipitation_sum: float | None = None
    precipitation_probability_max: float | None = None
    wind_speed_10m_max: float | None = None
    weather_code: int | None = None
    sunrise: datetime | None = None
    sunset: datetime | None = None


@dataclass(frozen=True)
class WeatherForecast:
    """Top-level structured weather forecast containing metadata and forecast series."""

    metadata: ForecastMetadata
    current: CurrentWeather
    hourly: tuple[HourlyForecast, ...] = ()
    daily: tuple[DailyForecast, ...] = ()
