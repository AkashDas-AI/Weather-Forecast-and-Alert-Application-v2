"""Unit tests for Phase 10 weather insights and interpretation layer.

All tests run offline without live API calls.
"""

from copy import deepcopy
from datetime import date, datetime

import pytest

from weather_app.alerts import evaluate_alerts
from weather_app.analysis import (
    INSIGHTS_DISCLAIMER,
    WeatherInsights,
    analyze_forecast,
    generate_weather_insights,
)
from weather_app.models import (
    CurrentWeather,
    DailyForecast,
    ForecastMetadata,
    HourlyForecast,
    WeatherForecast,
)


def _build_analysis_and_alerts(
    *,
    hourly: tuple[HourlyForecast, ...] = (),
    daily: tuple[DailyForecast, ...] = (),
    temp_c: float = 24.0,
    humidity_pct: float | None = 60.0,
    wind_kmh: float | None = 12.0,
    weather_code: int | None = 1,
    timezone: str = "Asia/Kolkata",
):
    forecast = WeatherForecast(
        metadata=ForecastMetadata(latitude=22.57, longitude=88.36, timezone=timezone),
        current=CurrentWeather(
            time=datetime(2026, 11, 27, 12, 0),
            temperature_2m=temp_c,
            relative_humidity_2m=humidity_pct,
            wind_speed_10m=wind_kmh,
            weather_code=weather_code,
        ),
        hourly=hourly,
        daily=daily,
    )
    analysis = analyze_forecast(forecast)
    evaluation = evaluate_alerts(analysis)
    return analysis, evaluation


class TestWeatherInsights:
    """Tests for Phase 10 rule-based insights generation."""

    def test_warming_pattern_daily_range_and_condition_transitions(self) -> None:
        hourly = (
            HourlyForecast(
                time=datetime(2026, 11, 27, 6, 0),
                temperature_2m=18.0,
                relative_humidity_2m=80.0,
                precipitation=0.0,
                precipitation_probability=15.0,
                wind_speed_10m=8.0,
                weather_code=1,
            ),
            HourlyForecast(
                time=datetime(2026, 11, 27, 9, 0),
                temperature_2m=22.0,
                relative_humidity_2m=70.0,
                precipitation=1.5,
                precipitation_probability=75.0,
                wind_speed_10m=16.0,
                weather_code=61,
            ),
        )
        daily = (
            DailyForecast(
                date=date(2026, 11, 27),
                temperature_2m_min=18.0,
                temperature_2m_max=28.0,
                precipitation_sum=1.5,
                precipitation_probability_max=75.0,
                wind_speed_10m_max=16.0,
                weather_code=61,
            ),
        )
        analysis, evaluation = _build_analysis_and_alerts(hourly=hourly, daily=daily)
        insights = generate_weather_insights(analysis, evaluation)

        assert isinstance(insights, WeatherInsights)
        assert insights.disclaimer == INSIGHTS_DISCLAIMER
        assert any("warming pattern" in s.lower() for s in insights.temperature_insights)
        assert any("10.0 °C" in s for s in insights.temperature_insights)
        assert any("1.5 mm" in s for s in insights.precipitation_insights)
        assert any("75%" in s and "not guaranteed" in s.lower() for s in insights.precipitation_insights)
        assert any("Mainly clear -> Slight rain" in s for s in insights.condition_insights)
        assert evaluation.total_count == 2
        assert any("2 educational advisory" in s for s in insights.advisory_insights)

    def test_cooling_pattern_and_no_alert_interpretation(self) -> None:
        hourly = (
            HourlyForecast(
                time=datetime(2026, 11, 27, 14, 0),
                temperature_2m=28.0,
                precipitation=0.0,
                precipitation_probability=10.0,
                weather_code=0,
            ),
            HourlyForecast(
                time=datetime(2026, 11, 27, 23, 0),
                temperature_2m=20.0,
                precipitation=0.0,
                precipitation_probability=10.0,
                weather_code=0,
            ),
        )
        analysis, evaluation = _build_analysis_and_alerts(hourly=hourly)
        insights = generate_weather_insights(analysis, evaluation)

        assert any("cooling pattern" in s.lower() for s in insights.temperature_insights)
        assert any("0.0 mm" in s for s in insights.precipitation_insights)
        assert any("No educational advisories were triggered" in s for s in insights.advisory_insights)

    def test_empty_forecast_and_missing_optional_fields(self) -> None:
        analysis, evaluation = _build_analysis_and_alerts(
            hourly=(),
            daily=(),
            temp_c=21.0,
            humidity_pct=None,
            wind_kmh=None,
            weather_code=None,
        )
        insights = generate_weather_insights(analysis, evaluation)

        assert any("Only the current temperature" in s for s in insights.temperature_insights)
        assert any("unavailable" in s.lower() for s in insights.precipitation_insights)
        assert any("unavailable" in s.lower() for s in insights.humidity_insights)
        assert any("unavailable" in s.lower() for s in insights.wind_insights)
        assert any("Unknown weather condition" in s for s in insights.condition_insights)

    def test_local_timestamp_preservation_determinism_and_immutability(self) -> None:
        hourly = (
            HourlyForecast(
                time=datetime(2026, 11, 27, 23, 30),
                temperature_2m=19.0,
                precipitation_probability=60.0,
                weather_code=2,
            ),
        )
        analysis, evaluation = _build_analysis_and_alerts(
            hourly=hourly,
            timezone="America/Los_Angeles",
        )
        analysis_before = deepcopy(analysis)
        eval_before = deepcopy(evaluation)

        first = generate_weather_insights(analysis, evaluation)
        second = generate_weather_insights(analysis, evaluation)

        assert first == second
        assert analysis == analysis_before
        assert evaluation == eval_before
        assert any("2026-11-27 23:30" in s for s in first.precipitation_insights)

    def test_invalid_inputs_raise_type_error(self) -> None:
        with pytest.raises(TypeError, match="ForecastAnalysis"):
            generate_weather_insights({"bad": True})  # type: ignore[arg-type]

        analysis, _ = _build_analysis_and_alerts()
        with pytest.raises(TypeError, match="AlertEvaluation"):
            generate_weather_insights(analysis, evaluation={"bad": True})  # type: ignore[arg-type]
