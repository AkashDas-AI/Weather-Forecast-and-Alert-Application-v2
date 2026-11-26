"""Unit tests for Phase 6 forecast analysis module.

All tests use constructed WeatherForecast instances or the local sample JSON
parsed via Phase 5; no live API calls are made.
"""

from datetime import date, datetime
import json
from pathlib import Path

import pytest

from weather_app.analysis import (
    ForecastAnalysis,
    UNKNOWN_WEATHER_DESCRIPTION,
    analyze_forecast,
    describe_weather_code,
)
from weather_app.models import (
    CurrentWeather,
    DailyForecast,
    ForecastMetadata,
    HourlyForecast,
    WeatherForecast,
)
from weather_app.services.weather_service import parse_forecast_response


def _build_forecast(
    hourly: tuple[HourlyForecast, ...] = (),
    daily: tuple[DailyForecast, ...] = (),
    current: CurrentWeather | None = None,
    timezone: str = "Asia/Kolkata",
) -> WeatherForecast:
    return WeatherForecast(
        metadata=ForecastMetadata(
            latitude=22.5726,
            longitude=88.3639,
            timezone=timezone,
        ),
        current=current
        or CurrentWeather(
            time=datetime(2026, 11, 27, 23, 30),
            temperature_2m=25.0,
            apparent_temperature=26.5,
            relative_humidity_2m=70.0,
            precipitation=0.2,
            wind_speed_10m=10.0,
            wind_direction_10m=180.0,
            weather_code=1,
        ),
        hourly=hourly,
        daily=daily,
    )


class TestWeatherCodeInterpretation:
    """Tests for describe_weather_code."""

    @pytest.mark.parametrize(
        "code,expected",
        [
            (0, "Clear sky"),
            (2, "Partly cloudy"),
            (45, "Fog"),
            (51, "Light drizzle"),
            (56, "Light freezing drizzle"),
            (63, "Moderate rain"),
            (66, "Light freezing rain"),
            (73, "Moderate snowfall"),
            (77, "Snow grains"),
            (80, "Slight rain showers"),
            (85, "Slight snow showers"),
            (95, "Thunderstorm"),
            (99, "Thunderstorm with heavy hail"),
        ],
    )
    def test_known_weather_codes(self, code: int, expected: str) -> None:
        assert describe_weather_code(code) == expected

    @pytest.mark.parametrize("unknown_code", [None, -1, 999, True])
    def test_unknown_weather_codes_return_safe_description(self, unknown_code) -> None:
        assert describe_weather_code(unknown_code) == UNKNOWN_WEATHER_DESCRIPTION


class TestForecastAnalysis:
    """Tests for analyze_forecast."""

    def test_sample_fixture_end_to_end_analysis(self) -> None:
        payload = json.loads(Path("data/sample/sample_weather.json").read_text(encoding="utf-8"))
        forecast = parse_forecast_response(payload)

        result = analyze_forecast(forecast)

        assert isinstance(result, ForecastAnalysis)
        assert result.timezone == "Asia/Kolkata"
        assert result.current.condition_description == "Mainly clear"
        assert result.temperature.hourly_avg_c == pytest.approx(24.2)
        assert result.temperature.hourly_min_c == 23.9
        assert result.temperature.hourly_max_c == 24.5
        assert result.temperature.daily_min_c == 19.8
        assert result.temperature.daily_max_c == 30.1
        assert result.humidity.hourly_avg_pct == pytest.approx(73.5)
        assert result.precipitation.daily_total_mm == pytest.approx(1.2)
        assert result.precipitation.daily_max_probability_pct == 35.0
        assert result.wind.hourly_avg_speed_kmh == pytest.approx(7.9)
        assert result.wind.daily_max_speed_kmh == 14.0
        assert len(result.daily_summaries) == 2

    def test_humidity_and_precipitation_with_missing_values(self) -> None:
        hourly = (
            HourlyForecast(
                time=datetime(2026, 11, 27, 1, 0),
                temperature_2m=20.0,
                relative_humidity_2m=None,
                precipitation=None,
                precipitation_probability=80.0,
                wind_speed_10m=None,
                weather_code=61,
            ),
            HourlyForecast(
                time=datetime(2026, 11, 27, 2, 0),
                temperature_2m=22.0,
                relative_humidity_2m=60.0,
                precipitation=2.5,
                precipitation_probability=None,
                wind_speed_10m=12.0,
                weather_code=0,
            ),
        )
        forecast = _build_forecast(hourly=hourly)
        result = analyze_forecast(forecast)

        # Missing values are excluded, never replaced with 0
        assert result.humidity.hourly_sample_count == 1
        assert result.humidity.hourly_avg_pct == 60.0
        assert result.humidity.hourly_min_pct == 60.0
        assert result.humidity.hourly_max_pct == 60.0

        # Precipitation amount (mm) vs probability (%) kept distinct
        assert result.precipitation.hourly_amount_count == 1
        assert result.precipitation.hourly_total_mm == 2.5
        assert result.precipitation.hourly_max_mm == 2.5
        assert result.precipitation.hourly_probability_count == 1
        assert result.precipitation.hourly_max_probability_pct == 80.0
        assert result.precipitation.hourly_avg_probability_pct == 80.0

        assert result.wind.hourly_sample_count == 1
        assert result.wind.hourly_avg_speed_kmh == 12.0
        assert result.wind.hourly_max_speed_kmh == 12.0

        # Every hourly record is preserved in hourly_summaries without threshold filtering
        assert len(result.hourly_summaries) == 2
        assert result.hourly_summaries[0].condition_description == "Slight rain"
        assert result.hourly_summaries[0].precipitation_mm is None
        assert result.hourly_summaries[0].precipitation_probability_pct == 80.0
        assert result.hourly_summaries[1].condition_description == "Clear sky"
        assert result.hourly_summaries[1].precipitation_mm == 2.5
        assert result.hourly_summaries[1].precipitation_probability_pct is None

    def test_empty_hourly_and_daily_tuples(self) -> None:
        current = CurrentWeather(
            time=datetime(2026, 11, 27, 10, 0),
            temperature_2m=18.5,
            apparent_temperature=None,
            relative_humidity_2m=None,
            precipitation=None,
            wind_speed_10m=None,
            wind_direction_10m=None,
            weather_code=None,
        )
        forecast = _build_forecast(hourly=(), daily=(), current=current)
        result = analyze_forecast(forecast)

        assert result.temperature.current_c == 18.5
        assert result.temperature.apparent_c is None
        assert result.temperature.hourly_avg_c is None
        assert result.temperature.daily_min_c is None
        assert result.temperature.has_sufficient_hourly_data is False
        assert result.temperature.has_sufficient_daily_data is False
        assert result.humidity.has_sufficient_data is False
        assert result.precipitation.hourly_total_mm is None
        assert result.wind.hourly_avg_speed_kmh is None
        assert result.daily_summaries == ()
        assert result.hourly_summaries == ()
        assert result.hourly_dates == ()
        assert result.current.condition_description == UNKNOWN_WEATHER_DESCRIPTION

    def test_hourly_summaries_preserve_zero_precipitation_and_all_records(self) -> None:
        hourly = (
            HourlyForecast(
                time=datetime(2026, 11, 27, 6, 0),
                temperature_2m=15.0,
                precipitation=0.0,
                precipitation_probability=0.0,
                wind_speed_10m=5.0,
                weather_code=0,
            ),
            HourlyForecast(
                time=datetime(2026, 11, 27, 7, 0),
                temperature_2m=16.5,
                precipitation=None,
                precipitation_probability=None,
                wind_speed_10m=None,
                weather_code=None,
            ),
        )
        forecast = _build_forecast(hourly=hourly)
        result = analyze_forecast(forecast)

        assert len(result.hourly_summaries) == 2
        assert result.hourly_summaries[0].precipitation_mm == 0.0
        assert result.hourly_summaries[0].precipitation_probability_pct == 0.0
        assert result.hourly_summaries[0].condition_description == "Clear sky"
        assert result.hourly_summaries[1].precipitation_mm is None
        assert result.hourly_summaries[1].wind_speed_kmh is None
        assert result.hourly_summaries[1].condition_description == UNKNOWN_WEATHER_DESCRIPTION

    def test_timezone_and_local_date_preservation(self) -> None:
        # Late-night naive local timestamps must stay on 2026-11-27 (never shifted to UTC)
        hourly = (
            HourlyForecast(
                time=datetime(2026, 11, 27, 23, 0),
                temperature_2m=21.0,
                precipitation_probability=60.0,
            ),
            HourlyForecast(
                time=datetime(2026, 11, 28, 0, 0),
                temperature_2m=20.5,
            ),
        )
        forecast = _build_forecast(hourly=hourly, timezone="America/Los_Angeles")
        result = analyze_forecast(forecast)

        assert result.timezone == "America/Los_Angeles"
        assert result.hourly_dates == (date(2026, 11, 27), date(2026, 11, 28))
        assert result.hourly_summaries[0].local_date == date(2026, 11, 27)
        assert result.hourly_summaries[0].time == datetime(2026, 11, 27, 23, 0)
        assert result.hourly_summaries[1].local_date == date(2026, 11, 28)

    def test_invalid_input_type_raises_type_error(self) -> None:
        with pytest.raises(TypeError, match="WeatherForecast"):
            analyze_forecast({"not": "a model"})  # type: ignore[arg-type]
