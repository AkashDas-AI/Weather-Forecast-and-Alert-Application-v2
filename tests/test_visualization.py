"""Unit tests for Phase 8 Plotly weather visualization functions.

All tests run offline without live API calls or graphical display.
"""

from copy import deepcopy
from datetime import date, datetime

import plotly.graph_objects as go
import pytest

from weather_app.analysis import UNKNOWN_WEATHER_DESCRIPTION, analyze_forecast
from weather_app.models import (
    CurrentWeather,
    DailyForecast,
    ForecastMetadata,
    HourlyForecast,
    WeatherForecast,
)
from weather_app.visualization import (
    create_daily_temperature_chart,
    create_humidity_chart,
    create_hourly_temperature_chart,
    create_precipitation_chart,
    create_weather_conditions_chart,
    create_wind_chart,
)


def _sample_forecast() -> WeatherForecast:
    return WeatherForecast(
        metadata=ForecastMetadata(latitude=22.57, longitude=88.36, timezone="Asia/Kolkata"),
        current=CurrentWeather(
            time=datetime(2026, 11, 27, 12, 0),
            temperature_2m=26.0,
            weather_code=1,
        ),
        hourly=(
            HourlyForecast(
                time=datetime(2026, 11, 27, 23, 0),
                temperature_2m=22.5,
                relative_humidity_2m=75.0,
                precipitation=0.0,
                precipitation_probability=20.0,
                wind_speed_10m=10.5,
                weather_code=1,
            ),
            HourlyForecast(
                time=datetime(2026, 11, 28, 0, 0),
                temperature_2m=21.0,
                relative_humidity_2m=None,
                precipitation=1.8,
                precipitation_probability=65.0,
                wind_speed_10m=None,
                weather_code=999,  # unknown code
            ),
        ),
        daily=(
            DailyForecast(
                date=date(2026, 11, 27),
                temperature_2m_min=19.0,
                temperature_2m_max=29.5,
            ),
            DailyForecast(
                date=date(2026, 11, 28),
                temperature_2m_min=20.0,
                temperature_2m_max=30.0,
            ),
        ),
    )


class TestWeatherVisualizations:
    """Tests for Phase 8 chart generation functions."""

    def test_hourly_and_daily_temperature_charts(self) -> None:
        forecast = _sample_forecast()
        analysis = analyze_forecast(forecast)

        hourly_fig = create_hourly_temperature_chart(forecast)
        daily_fig = create_daily_temperature_chart(analysis)

        assert isinstance(hourly_fig, go.Figure)
        assert list(hourly_fig.data[0].y) == [22.5, 21.0]
        assert list(hourly_fig.data[0].x) == [
            datetime(2026, 11, 27, 23, 0),
            datetime(2026, 11, 28, 0, 0),
        ]
        assert "°C" in hourly_fig.layout.yaxis.title.text

        assert isinstance(daily_fig, go.Figure)
        assert len(daily_fig.data) == 2
        assert list(daily_fig.data[0].y) == [29.5, 30.0]
        assert list(daily_fig.data[1].y) == [19.0, 20.0]

    def test_precipitation_chart_separates_amount_and_probability(self) -> None:
        forecast = _sample_forecast()
        fig = create_precipitation_chart(forecast)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 2
        amount_trace, prob_trace = fig.data[0], fig.data[1]
        assert isinstance(amount_trace, go.Bar)
        assert isinstance(prob_trace, go.Scatter)
        assert list(amount_trace.y) == [0.0, 1.8]
        assert list(prob_trace.y) == [20.0, 65.0]
        assert "mm" in fig.layout.yaxis.title.text
        assert "%" in fig.layout.yaxis2.title.text

    def test_humidity_and_wind_charts_preserve_none_gaps(self) -> None:
        forecast = _sample_forecast()
        hum_fig = create_humidity_chart(forecast)
        wind_fig = create_wind_chart(forecast)

        assert list(hum_fig.data[0].y) == [75.0, None]
        assert "%" in hum_fig.layout.yaxis.title.text
        assert list(wind_fig.data[0].y) == [10.5, None]
        assert "km/h" in wind_fig.layout.yaxis.title.text

    def test_weather_conditions_chart_handles_unknown_codes_safely(self) -> None:
        forecast = _sample_forecast()
        analysis = analyze_forecast(forecast)
        fig = create_weather_conditions_chart(analysis)

        assert isinstance(fig, go.Figure)
        assert list(fig.data[0].y) == ["Mainly clear", UNKNOWN_WEATHER_DESCRIPTION]

    def test_empty_data_returns_clean_empty_figures(self) -> None:
        empty_forecast = WeatherForecast(
            metadata=ForecastMetadata(latitude=22.57, longitude=88.36, timezone="Asia/Kolkata"),
            current=CurrentWeather(time=datetime(2026, 11, 27, 12, 0), temperature_2m=25.0),
            hourly=(),
            daily=(),
        )
        empty_analysis = analyze_forecast(empty_forecast)

        for fig in (
            create_hourly_temperature_chart(empty_forecast),
            create_daily_temperature_chart(empty_analysis),
            create_precipitation_chart(empty_forecast),
            create_humidity_chart(empty_forecast),
            create_wind_chart(empty_forecast),
            create_weather_conditions_chart(empty_analysis),
        ):
            assert isinstance(fig, go.Figure)
            assert len(fig.data) == 0
            assert len(fig.layout.annotations) == 1

    def test_inputs_not_mutated_and_invalid_types_rejected(self) -> None:
        forecast = _sample_forecast()
        analysis = analyze_forecast(forecast)
        forecast_before = deepcopy(forecast)
        analysis_before = deepcopy(analysis)

        create_hourly_temperature_chart(forecast)
        create_precipitation_chart(forecast)
        create_daily_temperature_chart(analysis)
        create_weather_conditions_chart(analysis)

        assert forecast == forecast_before
        assert analysis == analysis_before

        with pytest.raises(TypeError):
            create_hourly_temperature_chart({"bad": True})  # type: ignore[arg-type]
        with pytest.raises(TypeError):
            create_daily_temperature_chart({"bad": True})  # type: ignore[arg-type]

    @pytest.mark.parametrize("theme,expected_bg,expected_font", [
        ("dark", "#0f172a", "#f1f5f9"),
        ("light", "#ffffff", "#0f172a"),
    ])
    def test_all_six_charts_apply_dark_and_light_themes(
        self,
        theme: str,
        expected_bg: str,
        expected_font: str,
    ) -> None:
        forecast = _sample_forecast()
        analysis = analyze_forecast(forecast)
        figs = [
            create_hourly_temperature_chart(forecast, theme=theme),
            create_daily_temperature_chart(analysis, theme=theme),
            create_precipitation_chart(forecast, theme=theme),
            create_humidity_chart(forecast, theme=theme),
            create_wind_chart(forecast, theme=theme),
            create_weather_conditions_chart(analysis, theme=theme),
        ]
        for fig in figs:
            assert fig.layout.plot_bgcolor == expected_bg
            assert fig.layout.font.color == expected_font
            assert fig.layout.xaxis.gridcolor is not None
            assert fig.layout.yaxis.gridcolor is not None

    def test_invalid_chart_theme_raises_value_error(self) -> None:
        forecast = _sample_forecast()
        with pytest.raises(ValueError, match="Unsupported chart theme"):
            create_hourly_temperature_chart(forecast, theme="sepia")
