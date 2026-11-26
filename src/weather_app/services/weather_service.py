"""JSON parsing and validation services for Open-Meteo responses.

Author: Akash Das
"""

from typing import Any

from weather_app.core.exceptions import DataParsingError
from weather_app.models.weather import (
    CurrentWeather,
    DailyForecast,
    ForecastMetadata,
    HourlyForecast,
    LocationInfo,
    WeatherForecast,
)
from weather_app.utils.date_time import parse_iso_date, parse_iso_datetime


def _require_float(value: Any, field_name: str) -> float:
    """Validate and convert a required numeric value (excluding bool) to float."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DataParsingError(f"Field '{field_name}' must be a valid number.")
    return float(value)


def _optional_float(value: Any, field_name: str) -> float | None:
    """Validate and convert an optional numeric value (excluding bool) to float or None."""
    if value is None:
        return None
    return _require_float(value, field_name)


def _optional_int(value: Any, field_name: str) -> int | None:
    """Validate and convert an optional integer value (excluding bool) to int or None."""
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise DataParsingError(f"Field '{field_name}' must be an integer.")
    return value


def _optional_str(value: Any, field_name: str) -> str | None:
    """Validate an optional string value."""
    if value is None:
        return None
    if not isinstance(value, str):
        raise DataParsingError(f"Field '{field_name}' must be a string.")
    return value


def _validate_coordinates(latitude: Any, longitude: Any, prefix: str = "") -> tuple[float, float]:
    """Validate latitude [-90, 90] and longitude [-180, 180]."""
    lat = _require_float(latitude, f"{prefix}latitude")
    lon = _require_float(longitude, f"{prefix}longitude")
    if not (-90.0 <= lat <= 90.0):
        raise DataParsingError(f"Field '{prefix}latitude' must be between -90 and 90.")
    if not (-180.0 <= lon <= 180.0):
        raise DataParsingError(f"Field '{prefix}longitude' must be between -180 and 180.")
    return lat, lon


def _validate_series_lengths(section: dict[str, Any], section_name: str) -> int:
    """Ensure 'time' is a list and all present list arrays in section match its length."""
    if "time" not in section or not isinstance(section["time"], list):
        raise DataParsingError(f"Section '{section_name}' must contain a 'time' list.")
    expected_len = len(section["time"])
    for key, values in section.items():
        if not isinstance(values, list):
            raise DataParsingError(
                f"Field '{section_name}.{key}' must be a list."
            )
        if len(values) != expected_len:
            raise DataParsingError(
                f"Field '{section_name}.{key}' length ({len(values)}) does not match 'time' length ({expected_len})."
            )
    return expected_len


def _parse_current(raw_current: Any) -> CurrentWeather:
    """Parse the 'current' section of an Open-Meteo forecast payload."""
    if not isinstance(raw_current, dict):
        raise DataParsingError("Section 'current' must be a JSON object.")
    if "time" not in raw_current:
        raise DataParsingError("Missing required field 'current.time'.")
    if "temperature_2m" not in raw_current:
        raise DataParsingError("Missing required field 'current.temperature_2m'.")

    return CurrentWeather(
        time=parse_iso_datetime(raw_current["time"], "current.time"),
        temperature_2m=_require_float(raw_current["temperature_2m"], "current.temperature_2m"),
        relative_humidity_2m=_optional_float(
            raw_current.get("relative_humidity_2m"), "current.relative_humidity_2m"
        ),
        apparent_temperature=_optional_float(
            raw_current.get("apparent_temperature"), "current.apparent_temperature"
        ),
        precipitation=_optional_float(raw_current.get("precipitation"), "current.precipitation"),
        rain=_optional_float(raw_current.get("rain"), "current.rain"),
        wind_speed_10m=_optional_float(raw_current.get("wind_speed_10m"), "current.wind_speed_10m"),
        wind_direction_10m=_optional_float(
            raw_current.get("wind_direction_10m"), "current.wind_direction_10m"
        ),
        weather_code=_optional_int(raw_current.get("weather_code"), "current.weather_code"),
    )


def _parse_hourly(raw_hourly: Any) -> tuple[HourlyForecast, ...]:
    """Parse the 'hourly' section into a tuple of HourlyForecast records."""
    if raw_hourly is None:
        return ()
    if not isinstance(raw_hourly, dict):
        raise DataParsingError("Section 'hourly' must be a JSON object.")

    length = _validate_series_lengths(raw_hourly, "hourly")
    if "temperature_2m" not in raw_hourly:
        raise DataParsingError("Missing required field 'hourly.temperature_2m'.")

    times = raw_hourly["time"]
    temps = raw_hourly["temperature_2m"]
    humidities = raw_hourly.get("relative_humidity_2m")
    precip_probs = raw_hourly.get("precipitation_probability")
    precips = raw_hourly.get("precipitation")
    winds = raw_hourly.get("wind_speed_10m")
    wind_dirs = raw_hourly.get("wind_direction_10m")
    codes = raw_hourly.get("weather_code")

    records: list[HourlyForecast] = []
    for i in range(length):
        records.append(
            HourlyForecast(
                time=parse_iso_datetime(times[i], f"hourly.time[{i}]"),
                temperature_2m=_require_float(temps[i], f"hourly.temperature_2m[{i}]"),
                relative_humidity_2m=_optional_float(
                    humidities[i] if humidities is not None else None,
                    f"hourly.relative_humidity_2m[{i}]",
                ),
                precipitation_probability=_optional_float(
                    precip_probs[i] if precip_probs is not None else None,
                    f"hourly.precipitation_probability[{i}]",
                ),
                precipitation=_optional_float(
                    precips[i] if precips is not None else None,
                    f"hourly.precipitation[{i}]",
                ),
                wind_speed_10m=_optional_float(
                    winds[i] if winds is not None else None,
                    f"hourly.wind_speed_10m[{i}]",
                ),
                wind_direction_10m=_optional_float(
                    wind_dirs[i] if wind_dirs is not None else None,
                    f"hourly.wind_direction_10m[{i}]",
                ),
                weather_code=_optional_int(
                    codes[i] if codes is not None else None,
                    f"hourly.weather_code[{i}]",
                ),
            )
        )
    return tuple(records)


def _parse_daily(raw_daily: Any) -> tuple[DailyForecast, ...]:
    """Parse the 'daily' section into a tuple of DailyForecast records."""
    if raw_daily is None:
        return ()
    if not isinstance(raw_daily, dict):
        raise DataParsingError("Section 'daily' must be a JSON object.")

    length = _validate_series_lengths(raw_daily, "daily")
    if "temperature_2m_max" not in raw_daily:
        raise DataParsingError("Missing required field 'daily.temperature_2m_max'.")
    if "temperature_2m_min" not in raw_daily:
        raise DataParsingError("Missing required field 'daily.temperature_2m_min'.")

    dates = raw_daily["time"]
    t_max = raw_daily["temperature_2m_max"]
    t_min = raw_daily["temperature_2m_min"]
    precip_sum = raw_daily.get("precipitation_sum")
    precip_prob_max = raw_daily.get("precipitation_probability_max")
    wind_max = raw_daily.get("wind_speed_10m_max")
    codes = raw_daily.get("weather_code")
    sunrises = raw_daily.get("sunrise")
    sunsets = raw_daily.get("sunset")

    records: list[DailyForecast] = []
    for i in range(length):
        sunrise_val = sunrises[i] if sunrises is not None else None
        sunset_val = sunsets[i] if sunsets is not None else None
        records.append(
            DailyForecast(
                date=parse_iso_date(dates[i], f"daily.time[{i}]"),
                temperature_2m_max=_require_float(t_max[i], f"daily.temperature_2m_max[{i}]"),
                temperature_2m_min=_require_float(t_min[i], f"daily.temperature_2m_min[{i}]"),
                precipitation_sum=_optional_float(
                    precip_sum[i] if precip_sum is not None else None,
                    f"daily.precipitation_sum[{i}]",
                ),
                precipitation_probability_max=_optional_float(
                    precip_prob_max[i] if precip_prob_max is not None else None,
                    f"daily.precipitation_probability_max[{i}]",
                ),
                wind_speed_10m_max=_optional_float(
                    wind_max[i] if wind_max is not None else None,
                    f"daily.wind_speed_10m_max[{i}]",
                ),
                weather_code=_optional_int(
                    codes[i] if codes is not None else None,
                    f"daily.weather_code[{i}]",
                ),
                sunrise=(
                    parse_iso_datetime(sunrise_val, f"daily.sunrise[{i}]")
                    if sunrise_val is not None
                    else None
                ),
                sunset=(
                    parse_iso_datetime(sunset_val, f"daily.sunset[{i}]")
                    if sunset_val is not None
                    else None
                ),
            )
        )
    return tuple(records)


def parse_forecast_response(payload: dict[str, Any]) -> WeatherForecast:
    """Parse a raw Open-Meteo forecast JSON dictionary into a WeatherForecast model."""
    if not isinstance(payload, dict):
        raise DataParsingError("Forecast payload must be a JSON object.")

    for required_key in ("latitude", "longitude", "timezone", "current"):
        if required_key not in payload:
            raise DataParsingError(f"Missing required forecast field '{required_key}'.")

    lat, lon = _validate_coordinates(payload["latitude"], payload["longitude"])
    timezone = payload["timezone"]
    if not isinstance(timezone, str) or not timezone.strip():
        raise DataParsingError("Field 'timezone' must be a non-empty string.")

    metadata = ForecastMetadata(
        latitude=lat,
        longitude=lon,
        timezone=timezone.strip(),
        timezone_abbreviation=_optional_str(
            payload.get("timezone_abbreviation"), "timezone_abbreviation"
        ),
        elevation=_optional_float(payload.get("elevation"), "elevation"),
        utc_offset_seconds=_optional_int(payload.get("utc_offset_seconds"), "utc_offset_seconds"),
    )

    current = _parse_current(payload["current"])
    hourly = _parse_hourly(payload.get("hourly"))
    daily = _parse_daily(payload.get("daily"))

    return WeatherForecast(
        metadata=metadata,
        current=current,
        hourly=hourly,
        daily=daily,
    )


def parse_geocoding_response(payload: dict[str, Any]) -> list[LocationInfo]:
    """Parse a raw Open-Meteo geocoding JSON dictionary into LocationInfo objects."""
    if not isinstance(payload, dict):
        raise DataParsingError("Geocoding payload must be a JSON object.")

    results = payload.get("results")
    if not isinstance(results, list) or len(results) == 0:
        raise DataParsingError("Geocoding payload must contain a non-empty 'results' list.")

    locations: list[LocationInfo] = []
    for idx, item in enumerate(results):
        if not isinstance(item, dict):
            raise DataParsingError(f"Geocoding record at index {idx} must be a JSON object.")

        for req in ("name", "latitude", "longitude"):
            if req not in item:
                raise DataParsingError(f"Missing required field 'results[{idx}].{req}'.")

        name = item["name"]
        if not isinstance(name, str) or not name.strip():
            raise DataParsingError(f"Field 'results[{idx}].name' must be a non-empty string.")

        lat, lon = _validate_coordinates(
            item["latitude"], item["longitude"], prefix=f"results[{idx}]."
        )

        locations.append(
            LocationInfo(
                name=name.strip(),
                latitude=lat,
                longitude=lon,
                timezone=_optional_str(item.get("timezone"), f"results[{idx}].timezone"),
                country=_optional_str(item.get("country"), f"results[{idx}].country"),
                country_code=_optional_str(item.get("country_code"), f"results[{idx}].country_code"),
                admin1=_optional_str(item.get("admin1"), f"results[{idx}].admin1"),
                elevation=_optional_float(item.get("elevation"), f"results[{idx}].elevation"),
                population=_optional_int(item.get("population"), f"results[{idx}].population"),
                location_id=_optional_int(item.get("id"), f"results[{idx}].id"),
            )
        )

    return locations
