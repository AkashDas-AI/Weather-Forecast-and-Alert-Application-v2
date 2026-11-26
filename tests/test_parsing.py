"""Unit tests for Phase 5 JSON parsing and weather/location data models.

All tests use in-memory fixtures or local sample JSON; no live API calls are made.
"""

from datetime import date, datetime
import json
from pathlib import Path

import pytest

from weather_app.core.exceptions import DataParsingError
from weather_app.models import (
    CurrentWeather,
    DailyForecast,
    ForecastMetadata,
    HourlyForecast,
    LocationInfo,
    WeatherForecast,
)
from weather_app.services.weather_service import (
    parse_forecast_response,
    parse_geocoding_response,
)


def _valid_forecast_payload() -> dict:
    return {
        "latitude": 22.5726,
        "longitude": 88.3639,
        "utc_offset_seconds": 19800,
        "timezone": "Asia/Kolkata",
        "timezone_abbreviation": "IST",
        "elevation": 9.0,
        "current": {
            "time": "2026-11-27T00:00",
            "temperature_2m": 24.5,
            "relative_humidity_2m": 72,
            "apparent_temperature": 25.8,
            "precipitation": 0.0,
            "rain": 0.0,
            "wind_speed_10m": 8.2,
            "wind_direction_10m": 180,
            "weather_code": 1,
        },
        "hourly": {
            "time": ["2026-11-27T00:00", "2026-11-27T01:00"],
            "temperature_2m": [24.5, 23.9],
            "relative_humidity_2m": [72, 75],
            "precipitation_probability": [10, 15],
            "precipitation": [0.0, 0.0],
            "wind_speed_10m": [8.2, 7.6],
            "wind_direction_10m": [180, 175],
            "weather_code": [1, 2],
        },
        "daily": {
            "time": ["2026-11-27", "2026-11-28"],
            "temperature_2m_max": [29.5, 30.1],
            "temperature_2m_min": [19.8, 20.2],
            "precipitation_sum": [0.0, 1.2],
            "precipitation_probability_max": [15, 35],
            "wind_speed_10m_max": [12.4, 14.0],
            "weather_code": [1, 3],
            "sunrise": ["2026-11-27T05:56", "2026-11-28T05:57"],
            "sunset": ["2026-11-27T16:51", "2026-11-28T16:51"],
        },
    }


class TestForecastParsing:
    """Tests for parse_forecast_response and weather models."""

    def test_valid_combined_forecast_and_sample_file(self) -> None:
        sample_path = Path("data/sample/sample_weather.json")
        payload = json.loads(sample_path.read_text(encoding="utf-8"))

        forecast = parse_forecast_response(payload)

        assert isinstance(forecast, WeatherForecast)
        assert isinstance(forecast.metadata, ForecastMetadata)
        assert forecast.metadata.latitude == 22.5726
        assert forecast.metadata.longitude == 88.3639
        assert forecast.metadata.timezone == "Asia/Kolkata"

        assert isinstance(forecast.current, CurrentWeather)
        assert forecast.current.time == datetime(2026, 11, 27, 0, 0)
        assert forecast.current.temperature_2m == 24.5

        assert len(forecast.hourly) == 2
        assert isinstance(forecast.hourly[0], HourlyForecast)
        assert forecast.hourly[1].temperature_2m == 23.9

        assert len(forecast.daily) == 2
        assert isinstance(forecast.daily[0], DailyForecast)
        assert forecast.daily[0].date == date(2026, 11, 27)
        assert forecast.daily[0].sunrise == datetime(2026, 11, 27, 5, 56)

    def test_valid_current_only_with_optional_fields_missing_or_null(self) -> None:
        payload = {
            "latitude": 51.5,
            "longitude": -0.12,
            "timezone": "Europe/London",
            "current": {
                "time": "2026-11-27T12:00",
                "temperature_2m": 11.4,
                "relative_humidity_2m": None,
            },
        }
        forecast = parse_forecast_response(payload)

        assert forecast.current.temperature_2m == 11.4
        assert forecast.current.relative_humidity_2m is None
        assert forecast.current.wind_speed_10m is None
        assert forecast.hourly == ()
        assert forecast.daily == ()

    def test_valid_hourly_with_null_optional_elements(self) -> None:
        payload = _valid_forecast_payload()
        payload["hourly"]["precipitation_probability"] = [10, None]
        payload["hourly"].pop("wind_direction_10m")

        forecast = parse_forecast_response(payload)
        assert forecast.hourly[0].precipitation_probability == 10.0
        assert forecast.hourly[1].precipitation_probability is None
        assert forecast.hourly[0].wind_direction_10m is None

    def test_valid_daily_with_null_sunrise_sunset(self) -> None:
        payload = _valid_forecast_payload()
        payload["daily"]["sunrise"] = [None, "2026-11-28T05:57"]
        payload["daily"].pop("sunset")

        forecast = parse_forecast_response(payload)
        assert forecast.daily[0].sunrise is None
        assert forecast.daily[1].sunrise == datetime(2026, 11, 28, 5, 57)
        assert forecast.daily[0].sunset is None

    @pytest.mark.parametrize("missing_key", ["latitude", "longitude", "timezone", "current"])
    def test_missing_required_top_level_sections(self, missing_key: str) -> None:
        payload = _valid_forecast_payload()
        del payload[missing_key]

        with pytest.raises(DataParsingError, match=missing_key):
            parse_forecast_response(payload)

    def test_missing_required_current_fields(self) -> None:
        payload = _valid_forecast_payload()
        del payload["current"]["temperature_2m"]

        with pytest.raises(DataParsingError, match="current.temperature_2m"):
            parse_forecast_response(payload)

    @pytest.mark.parametrize("lat,lon", [(-95.0, 0.0), (95.0, 0.0), (0.0, -185.0), (0.0, 185.0)])
    def test_invalid_coordinates(self, lat: float, lon: float) -> None:
        payload = _valid_forecast_payload()
        payload["latitude"] = lat
        payload["longitude"] = lon

        with pytest.raises(DataParsingError):
            parse_forecast_response(payload)

    def test_invalid_data_types(self) -> None:
        payload = _valid_forecast_payload()
        payload["current"]["temperature_2m"] = "warm"

        with pytest.raises(DataParsingError, match="current.temperature_2m"):
            parse_forecast_response(payload)

    def test_mismatched_hourly_array_lengths(self) -> None:
        payload = _valid_forecast_payload()
        payload["hourly"]["temperature_2m"] = [24.5]

        with pytest.raises(DataParsingError, match="hourly.temperature_2m"):
            parse_forecast_response(payload)

    def test_mismatched_daily_array_lengths(self) -> None:
        payload = _valid_forecast_payload()
        payload["daily"]["temperature_2m_max"] = [29.5]

        with pytest.raises(DataParsingError, match="daily.temperature_2m_max"):
            parse_forecast_response(payload)

    def test_datetime_parsing_errors(self) -> None:
        payload = _valid_forecast_payload()
        payload["current"]["time"] = "not-a-timestamp"

        with pytest.raises(DataParsingError, match="current.time"):
            parse_forecast_response(payload)

    def test_daily_date_parsing_error(self) -> None:
        payload = _valid_forecast_payload()
        payload["daily"]["time"] = ["2026/11/27", "2026-11-28"]

        with pytest.raises(DataParsingError, match="daily.time"):
            parse_forecast_response(payload)


class TestGeocodingParsing:
    """Tests for parse_geocoding_response and LocationInfo."""

    def test_valid_geocoding_results(self) -> None:
        payload = {
            "results": [
                {
                    "id": 1275004,
                    "name": "Kolkata",
                    "latitude": 22.56263,
                    "longitude": 88.36304,
                    "elevation": 9.0,
                    "country_code": "IN",
                    "timezone": "Asia/Kolkata",
                    "population": 4631392,
                    "country": "India",
                    "admin1": "West Bengal",
                },
                {
                    "name": "Kolkata Minimal",
                    "latitude": 22.5,
                    "longitude": 88.3,
                },
            ]
        }

        locations = parse_geocoding_response(payload)

        assert len(locations) == 2
        assert isinstance(locations[0], LocationInfo)
        assert locations[0].name == "Kolkata"
        assert locations[0].country == "India"
        assert locations[0].admin1 == "West Bengal"
        assert locations[0].location_id == 1275004
        assert locations[1].country is None
        assert locations[1].population is None

    def test_geocoding_missing_required_field(self) -> None:
        payload = {"results": [{"name": "Kolkata", "latitude": 22.5}]}

        with pytest.raises(DataParsingError, match="longitude"):
            parse_geocoding_response(payload)

    def test_geocoding_invalid_coordinates(self) -> None:
        payload = {"results": [{"name": "Nowhere", "latitude": 120.0, "longitude": 10.0}]}

        with pytest.raises(DataParsingError, match="latitude"):
            parse_geocoding_response(payload)

    def test_geocoding_malformed_record_type(self) -> None:
        payload = {"results": ["not-a-dict"]}

        with pytest.raises(DataParsingError, match="index 0"):
            parse_geocoding_response(payload)
