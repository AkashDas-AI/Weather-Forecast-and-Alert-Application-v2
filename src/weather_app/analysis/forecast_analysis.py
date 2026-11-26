"""Forecast analysis module for structured WeatherForecast models.

Author: Akash Das
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable

from weather_app.models.weather import (
    CurrentWeather,
    DailyForecast,
    HourlyForecast,
    WeatherForecast,
)

WMO_WEATHER_CODES: dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

UNKNOWN_WEATHER_DESCRIPTION = "Unknown weather condition"


def describe_weather_code(code: int | None) -> str:
    """Return a human-readable description for a WMO/Open-Meteo weather code."""
    if code is None or isinstance(code, bool) or not isinstance(code, int):
        return UNKNOWN_WEATHER_DESCRIPTION
    return WMO_WEATHER_CODES.get(code, UNKNOWN_WEATHER_DESCRIPTION)


@dataclass(frozen=True)
class CurrentConditionSummary:
    """Summary of current weather conditions."""

    time: datetime
    temperature_c: float
    apparent_temperature_c: float | None
    relative_humidity_pct: float | None
    precipitation_mm: float | None
    wind_speed_kmh: float | None
    wind_direction_deg: float | None
    weather_code: int | None
    condition_description: str


@dataclass(frozen=True)
class TemperatureAnalysis:
    """Temperature statistics across current, hourly, and daily records."""

    current_c: float
    apparent_c: float | None
    hourly_avg_c: float | None
    hourly_min_c: float | None
    hourly_max_c: float | None
    daily_min_c: float | None
    daily_max_c: float | None
    hourly_sample_count: int
    daily_sample_count: int
    has_sufficient_hourly_data: bool
    has_sufficient_daily_data: bool


@dataclass(frozen=True)
class HumidityAnalysis:
    """Relative humidity summary across current and hourly observations."""

    current_pct: float | None
    hourly_avg_pct: float | None
    hourly_min_pct: float | None
    hourly_max_pct: float | None
    hourly_sample_count: int
    has_sufficient_data: bool


@dataclass(frozen=True)
class PrecipitationAnalysis:
    """Precipitation amount (mm) and probability (%) summary."""

    current_mm: float | None
    hourly_total_mm: float | None
    hourly_max_mm: float | None
    hourly_max_probability_pct: float | None
    hourly_avg_probability_pct: float | None
    daily_total_mm: float | None
    daily_max_probability_pct: float | None
    hourly_amount_count: int
    hourly_probability_count: int
    daily_amount_count: int


@dataclass(frozen=True)
class WindAnalysis:
    """Wind speed (km/h) and direction summary without severity inference."""

    current_speed_kmh: float | None
    current_direction_deg: float | None
    hourly_avg_speed_kmh: float | None
    hourly_max_speed_kmh: float | None
    daily_max_speed_kmh: float | None
    hourly_sample_count: int
    daily_sample_count: int


@dataclass(frozen=True)
class DailyConditionSummary:
    """Daily forecast summary with interpreted weather description."""

    date: date
    temp_min_c: float
    temp_max_c: float
    precipitation_sum_mm: float | None
    precipitation_probability_max_pct: float | None
    wind_speed_max_kmh: float | None
    weather_code: int | None
    condition_description: str


@dataclass(frozen=True)
class HourlyNotableCondition:
    """Hourly record flagged for notable descriptive weather conditions."""

    time: datetime
    local_date: date
    temperature_c: float
    precipitation_mm: float | None
    precipitation_probability_pct: float | None
    wind_speed_kmh: float | None
    weather_code: int | None
    condition_description: str
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class ForecastAnalysis:
    """Top-level structured forecast analysis output."""

    timezone: str
    latitude: float
    longitude: float
    current: CurrentConditionSummary
    temperature: TemperatureAnalysis
    humidity: HumidityAnalysis
    precipitation: PrecipitationAnalysis
    wind: WindAnalysis
    daily_summaries: tuple[DailyConditionSummary, ...]
    hourly_notable: tuple[HourlyNotableCondition, ...]
    hourly_dates: tuple[date, ...]


def _numeric_stats(
    values: Iterable[float | None],
) -> tuple[float | None, float | None, float | None, int]:
    """Compute (mean, min, max, count) over non-None numeric values."""
    valid = [float(v) for v in values if v is not None]
    if not valid:
        return None, None, None, 0
    return sum(valid) / len(valid), min(valid), max(valid), len(valid)


def _numeric_sum(values: Iterable[float | None]) -> tuple[float | None, int]:
    """Compute (sum, count) over non-None numeric values."""
    valid = [float(v) for v in values if v is not None]
    if not valid:
        return None, 0
    return sum(valid), len(valid)


def _analyze_current(current: CurrentWeather) -> CurrentConditionSummary:
    return CurrentConditionSummary(
        time=current.time,
        temperature_c=current.temperature_2m,
        apparent_temperature_c=current.apparent_temperature,
        relative_humidity_pct=current.relative_humidity_2m,
        precipitation_mm=current.precipitation,
        wind_speed_kmh=current.wind_speed_10m,
        wind_direction_deg=current.wind_direction_10m,
        weather_code=current.weather_code,
        condition_description=describe_weather_code(current.weather_code),
    )


def _analyze_temperature(
    current: CurrentWeather,
    hourly: tuple[HourlyForecast, ...],
    daily: tuple[DailyForecast, ...],
) -> TemperatureAnalysis:
    h_avg, h_min, h_max, h_count = _numeric_stats(h.temperature_2m for h in hourly)
    _, _, d_max, d_max_count = _numeric_stats(d.temperature_2m_max for d in daily)
    _, d_min, _, d_min_count = _numeric_stats(d.temperature_2m_min for d in daily)
    d_count = min(d_max_count, d_min_count)

    return TemperatureAnalysis(
        current_c=current.temperature_2m,
        apparent_c=current.apparent_temperature,
        hourly_avg_c=h_avg,
        hourly_min_c=h_min,
        hourly_max_c=h_max,
        daily_min_c=d_min,
        daily_max_c=d_max,
        hourly_sample_count=h_count,
        daily_sample_count=d_count,
        has_sufficient_hourly_data=h_count > 0,
        has_sufficient_daily_data=d_count > 0,
    )


def _analyze_humidity(
    current: CurrentWeather,
    hourly: tuple[HourlyForecast, ...],
) -> HumidityAnalysis:
    h_avg, h_min, h_max, h_count = _numeric_stats(h.relative_humidity_2m for h in hourly)
    return HumidityAnalysis(
        current_pct=current.relative_humidity_2m,
        hourly_avg_pct=h_avg,
        hourly_min_pct=h_min,
        hourly_max_pct=h_max,
        hourly_sample_count=h_count,
        has_sufficient_data=h_count > 0,
    )


def _analyze_precipitation(
    current: CurrentWeather,
    hourly: tuple[HourlyForecast, ...],
    daily: tuple[DailyForecast, ...],
) -> PrecipitationAnalysis:
    h_total, h_amt_count = _numeric_sum(h.precipitation for h in hourly)
    _, _, h_max_mm, _ = _numeric_stats(h.precipitation for h in hourly)
    h_prob_avg, _, h_prob_max, h_prob_count = _numeric_stats(
        h.precipitation_probability for h in hourly
    )
    d_total, d_amt_count = _numeric_sum(d.precipitation_sum for d in daily)
    _, _, d_prob_max, _ = _numeric_stats(d.precipitation_probability_max for d in daily)

    return PrecipitationAnalysis(
        current_mm=current.precipitation,
        hourly_total_mm=h_total,
        hourly_max_mm=h_max_mm,
        hourly_max_probability_pct=h_prob_max,
        hourly_avg_probability_pct=h_prob_avg,
        daily_total_mm=d_total,
        daily_max_probability_pct=d_prob_max,
        hourly_amount_count=h_amt_count,
        hourly_probability_count=h_prob_count,
        daily_amount_count=d_amt_count,
    )


def _analyze_wind(
    current: CurrentWeather,
    hourly: tuple[HourlyForecast, ...],
    daily: tuple[DailyForecast, ...],
) -> WindAnalysis:
    h_avg, _, h_max, h_count = _numeric_stats(h.wind_speed_10m for h in hourly)
    _, _, d_max, d_count = _numeric_stats(d.wind_speed_10m_max for d in daily)

    return WindAnalysis(
        current_speed_kmh=current.wind_speed_10m,
        current_direction_deg=current.wind_direction_10m,
        hourly_avg_speed_kmh=h_avg,
        hourly_max_speed_kmh=h_max,
        daily_max_speed_kmh=d_max,
        hourly_sample_count=h_count,
        daily_sample_count=d_count,
    )


def _summarize_daily(daily: tuple[DailyForecast, ...]) -> tuple[DailyConditionSummary, ...]:
    return tuple(
        DailyConditionSummary(
            date=d.date,
            temp_min_c=d.temperature_2m_min,
            temp_max_c=d.temperature_2m_max,
            precipitation_sum_mm=d.precipitation_sum,
            precipitation_probability_max_pct=d.precipitation_probability_max,
            wind_speed_max_kmh=d.wind_speed_10m_max,
            weather_code=d.weather_code,
            condition_description=describe_weather_code(d.weather_code),
        )
        for d in daily
    )


def _summarize_hourly_notable(
    hourly: tuple[HourlyForecast, ...],
) -> tuple[HourlyNotableCondition, ...]:
    notable: list[HourlyNotableCondition] = []
    for h in hourly:
        reasons: list[str] = []
        if h.precipitation is not None and h.precipitation > 0.0:
            reasons.append("precipitation_observed")
        if h.precipitation_probability is not None and h.precipitation_probability >= 50.0:
            reasons.append("elevated_precipitation_probability")
        if h.weather_code is not None and h.weather_code >= 51:
            reasons.append("notable_weather_code")

        if reasons:
            notable.append(
                HourlyNotableCondition(
                    time=h.time,
                    local_date=h.time.date(),
                    temperature_c=h.temperature_2m,
                    precipitation_mm=h.precipitation,
                    precipitation_probability_pct=h.precipitation_probability,
                    wind_speed_kmh=h.wind_speed_10m,
                    weather_code=h.weather_code,
                    condition_description=describe_weather_code(h.weather_code),
                    reasons=tuple(reasons),
                )
            )
    return tuple(notable)


def analyze_forecast(forecast: WeatherForecast) -> ForecastAnalysis:
    """Analyze a structured WeatherForecast and return a ForecastAnalysis summary."""
    if not isinstance(forecast, WeatherForecast):
        raise TypeError("forecast must be a WeatherForecast instance.")

    hourly_dates = tuple(dict.fromkeys(h.time.date() for h in forecast.hourly))

    return ForecastAnalysis(
        timezone=forecast.metadata.timezone,
        latitude=forecast.metadata.latitude,
        longitude=forecast.metadata.longitude,
        current=_analyze_current(forecast.current),
        temperature=_analyze_temperature(forecast.current, forecast.hourly, forecast.daily),
        humidity=_analyze_humidity(forecast.current, forecast.hourly),
        precipitation=_analyze_precipitation(forecast.current, forecast.hourly, forecast.daily),
        wind=_analyze_wind(forecast.current, forecast.hourly, forecast.daily),
        daily_summaries=_summarize_daily(forecast.daily),
        hourly_notable=_summarize_hourly_notable(forecast.hourly),
        hourly_dates=hourly_dates,
    )
