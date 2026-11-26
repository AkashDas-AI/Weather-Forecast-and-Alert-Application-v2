"""Unit tests for Phase 7 weather alert thresholds and alert engine.

All tests use constructed Phase 6 analysis models; no live API calls are made.
"""

from datetime import date, datetime
import math

import pytest

from weather_app.alerts import (
    AlertCategory,
    AlertEvaluation,
    AlertScope,
    AlertSeverity,
    AlertThresholds,
    EDUCATIONAL_DISCLAIMER,
    evaluate_alerts,
)
from weather_app.analysis import (
    CurrentConditionSummary,
    DailyConditionSummary,
    ForecastAnalysis,
    HourlyConditionSummary,
    HumidityAnalysis,
    PrecipitationAnalysis,
    TemperatureAnalysis,
    WindAnalysis,
    analyze_forecast,
)
from weather_app.core.exceptions import ConfigurationError
from weather_app.models import (
    CurrentWeather,
    DailyForecast,
    ForecastMetadata,
    HourlyForecast,
    WeatherForecast,
)


def _make_analysis(
    *,
    temp_c: float = 22.0,
    humidity_pct: float | None = 50.0,
    precip_mm: float | None = 0.0,
    wind_kmh: float | None = 10.0,
    weather_code: int | None = 0,
    hourly: tuple[HourlyForecast, ...] = (),
    daily: tuple[DailyForecast, ...] = (),
) -> ForecastAnalysis:
    forecast = WeatherForecast(
        metadata=ForecastMetadata(latitude=22.57, longitude=88.36, timezone="Asia/Kolkata"),
        current=CurrentWeather(
            time=datetime(2026, 11, 27, 12, 0),
            temperature_2m=temp_c,
            relative_humidity_2m=humidity_pct,
            precipitation=precip_mm,
            wind_speed_10m=wind_kmh,
            weather_code=weather_code,
        ),
        hourly=hourly,
        daily=daily,
    )
    return analyze_forecast(forecast)


class TestAlertThresholds:
    """Tests for AlertThresholds defaults and validation."""

    def test_default_thresholds_are_valid(self) -> None:
        t = AlertThresholds()
        assert t.high_temp_c == 35.0
        assert t.low_temp_c == 5.0
        assert t.heavy_rain_hourly_mm == 10.0
        assert t.heavy_rain_daily_mm == 50.0
        assert t.high_precip_probability_pct == 70.0
        assert t.high_humidity_pct == 85.0
        assert t.strong_wind_kmh == 50.0
        assert 95 in t.severe_weather_codes

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"low_temp_c": 35.0, "high_temp_c": 35.0},
            {"low_temp_c": 40.0, "high_temp_c": 30.0},
            {"heavy_rain_hourly_mm": 0.0},
            {"heavy_rain_daily_mm": -5.0},
            {"high_precip_probability_pct": 101.0},
            {"high_humidity_pct": -1.0},
            {"strong_wind_kmh": 0.0},
            {"high_temp_c": True},
            {"high_temp_c": False},
            {"high_temp_c": "35"},
            {"high_temp_c": None},
            {"high_temp_c": math.nan},
            {"high_temp_c": math.inf},
            {"low_temp_c": -math.inf},
            {"high_temp_c": 10**400},
            {"low_temp_c": -(10**400)},
            {"severe_weather_codes": ()},
            {"severe_weather_codes": (95, True)},
            {"severe_weather_codes": (95, "96")},
            {"severe_weather_codes": (95, 95)},
        ],
    )
    def test_invalid_threshold_configuration_raises(self, kwargs: dict) -> None:
        with pytest.raises(ConfigurationError):
            AlertThresholds(**kwargs)

    def test_valid_integer_thresholds_accepted(self) -> None:
        t = AlertThresholds(high_temp_c=35, low_temp_c=5, strong_wind_kmh=50)
        assert t.high_temp_c == 35
        assert t.low_temp_c == 5
        assert t.strong_wind_kmh == 50

    def test_severe_weather_codes_list_normalized_to_immutable_tuple(self) -> None:
        codes = [95, 96]
        t = AlertThresholds(severe_weather_codes=codes)  # type: ignore[arg-type]
        codes.append(99)

        assert isinstance(t.severe_weather_codes, tuple)
        assert t.severe_weather_codes == (95, 96)


class TestAlertEngine:
    """Tests for evaluate_alerts."""

    def test_no_alerts_when_conditions_below_thresholds(self) -> None:
        analysis = _make_analysis(
            temp_c=22.0,
            humidity_pct=55.0,
            precip_mm=0.0,
            wind_kmh=12.0,
            weather_code=1,
            hourly=(
                HourlyForecast(
                    time=datetime(2026, 11, 27, 13, 0),
                    temperature_2m=23.0,
                    precipitation=0.5,
                    precipitation_probability=20.0,
                    wind_speed_10m=15.0,
                    weather_code=2,
                ),
            ),
            daily=(
                DailyForecast(
                    date=date(2026, 11, 27),
                    temperature_2m_min=16.0,
                    temperature_2m_max=28.0,
                    precipitation_sum=1.0,
                    precipitation_probability_max=25.0,
                    wind_speed_10m_max=20.0,
                    weather_code=2,
                ),
            ),
        )
        result = evaluate_alerts(analysis)

        assert isinstance(result, AlertEvaluation)
        assert result.total_count == 0
        assert result.alerts == ()
        assert result.disclaimer == EDUCATIONAL_DISCLAIMER

    def test_all_categories_and_severities_triggered(self) -> None:
        analysis = _make_analysis(
            temp_c=35.0,  # boundary high_temp_c -> ADVISORY
            humidity_pct=85.0,  # boundary high_humidity_pct -> INFO
            precip_mm=10.0,  # boundary heavy_rain_hourly_mm -> ADVISORY
            wind_kmh=50.0,  # boundary strong_wind_kmh -> ADVISORY
            weather_code=95,  # thunderstorm -> WARNING
            hourly=(
                HourlyForecast(
                    time=datetime(2026, 11, 27, 14, 0),
                    temperature_2m=5.0,  # boundary low_temp_c -> ADVISORY
                    precipitation=0.0,
                    precipitation_probability=70.0,  # boundary -> INFO
                    wind_speed_10m=20.0,
                    weather_code=65,  # heavy rain -> ADVISORY
                ),
            ),
            daily=(
                DailyForecast(
                    date=date(2026, 11, 28),
                    temperature_2m_min=4.0,
                    temperature_2m_max=36.0,
                    precipitation_sum=50.0,  # boundary -> ADVISORY
                    precipitation_probability_max=80.0,  # -> INFO
                    wind_speed_10m_max=60.0,  # -> ADVISORY
                    weather_code=99,  # hail thunderstorm -> WARNING
                ),
            ),
        )

        result = evaluate_alerts(analysis)
        categories = {a.category for a in result.alerts}
        severities = {a.severity for a in result.alerts}
        scopes = {a.scope for a in result.alerts}

        assert categories == {
            AlertCategory.HIGH_TEMPERATURE,
            AlertCategory.LOW_TEMPERATURE,
            AlertCategory.PRECIPITATION,
            AlertCategory.HIGH_HUMIDITY,
            AlertCategory.STRONG_WIND,
            AlertCategory.WEATHER_CONDITION,
        }
        assert severities == {AlertSeverity.INFO, AlertSeverity.ADVISORY, AlertSeverity.WARNING}
        assert scopes == {AlertScope.CURRENT, AlertScope.HOURLY, AlertScope.DAILY}

    def test_custom_thresholds_override_defaults(self) -> None:
        analysis = _make_analysis(temp_c=29.0, wind_kmh=25.0)
        assert evaluate_alerts(analysis).total_count == 0

        custom = AlertThresholds(high_temp_c=28.0, strong_wind_kmh=20.0)
        result = evaluate_alerts(analysis, thresholds=custom)
        assert result.total_count == 2
        assert result.thresholds == custom

    def test_missing_measurements_do_not_trigger_alerts(self) -> None:
        analysis = _make_analysis(
            temp_c=20.0,
            humidity_pct=None,
            precip_mm=None,
            wind_kmh=None,
            weather_code=None,
        )
        result = evaluate_alerts(analysis)
        assert result.total_count == 0

    def test_duplicate_prevention_for_identical_hourly_observations(self) -> None:
        dup_hour = HourlyForecast(
            time=datetime(2026, 11, 27, 15, 0),
            temperature_2m=38.0,
            wind_speed_10m=55.0,
        )
        analysis = _make_analysis(hourly=(dup_hour, dup_hour))
        result = evaluate_alerts(analysis)

        hourly_ids = [a.alert_id for a in result.alerts if a.scope == AlertScope.HOURLY]
        assert len(hourly_ids) == len(set(hourly_ids)) == 2

    def test_invalid_inputs_raise_type_error(self) -> None:
        with pytest.raises(TypeError, match="ForecastAnalysis"):
            evaluate_alerts({"invalid": True})  # type: ignore[arg-type]

        analysis = _make_analysis()
        with pytest.raises(TypeError, match="AlertThresholds"):
            evaluate_alerts(analysis, thresholds={"high_temp_c": 30})  # type: ignore[arg-type]
