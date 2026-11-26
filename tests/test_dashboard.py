"""Tests for Phase 9 Streamlit dashboard and forecast_service orchestration.

All API and geocoding operations are mocked; no live API calls or browser
sessions are required.
"""

from datetime import date, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")

from weather_app.alerts import AlertThresholds
from weather_app.core.exceptions import APITimeoutError, LocationNotFoundError
from weather_app.models import LocationInfo
from weather_app.services.forecast_service import (
    DashboardWeatherBundle,
    format_location_label,
    get_weather_dashboard_data,
    search_locations,
)


def _mock_geocoding_payload() -> dict:
    return {
        "results": [
            {
                "id": 1275004,
                "name": "Kolkata",
                "latitude": 22.56263,
                "longitude": 88.36304,
                "country": "India",
                "country_code": "IN",
                "admin1": "West Bengal",
                "timezone": "Asia/Kolkata",
            }
        ]
    }


def _mock_forecast_payload() -> dict:
    return {
        "latitude": 22.56263,
        "longitude": 88.36304,
        "timezone": "Asia/Kolkata",
        "current": {
            "time": "2026-11-27T12:00",
            "temperature_2m": 36.0,
            "relative_humidity_2m": 65,
            "apparent_temperature": 38.0,
            "precipitation": 0.0,
            "wind_speed_10m": 12.0,
            "wind_direction_10m": 180,
            "weather_code": 1,
        },
        "hourly": {
            "time": ["2026-11-27T12:00", "2026-11-27T13:00"],
            "temperature_2m": [36.0, 36.5],
            "relative_humidity_2m": [65, 62],
            "precipitation_probability": [10, 15],
            "precipitation": [0.0, 0.0],
            "wind_speed_10m": [12.0, 14.0],
            "wind_direction_10m": [180, 185],
            "weather_code": [1, 2],
        },
        "daily": {
            "time": ["2026-11-27"],
            "temperature_2m_max": [36.5],
            "temperature_2m_min": [22.0],
            "precipitation_sum": [0.0],
            "precipitation_probability_max": [15],
            "wind_speed_10m_max": [14.0],
            "weather_code": [1],
        },
    }


class TestForecastServiceOrchestration:
    """Tests for forecast_service functions used by the Streamlit dashboard."""

    def test_search_locations_returns_parsed_models(self) -> None:
        mock_geo = MagicMock()
        mock_geo.search_location.return_value = _mock_geocoding_payload()

        locations = search_locations("Kolkata", geocoding_client=mock_geo)

        assert len(locations) == 1
        assert isinstance(locations[0], LocationInfo)
        assert format_location_label(locations[0]) == "Kolkata, West Bengal, India (22.56, 88.36)"

    def test_get_weather_dashboard_data_pipeline(self) -> None:
        mock_client = MagicMock()
        mock_client.fetch_forecast.return_value = _mock_forecast_payload()

        bundle = get_weather_dashboard_data(
            22.56263,
            88.36304,
            weather_client=mock_client,
            thresholds=AlertThresholds(),
        )

        assert isinstance(bundle, DashboardWeatherBundle)
        assert bundle.analysis.current.temperature_c == 36.0
        assert bundle.alert_evaluation.total_count > 0  # >= 35.0 °C triggers high temp advisory


class TestStreamlitDashboardApp:
    """Headless AppTest tests for app.py."""

    def test_initial_render_prompts_for_location(self) -> None:
        at = AppTest.from_file(APP_PATH, default_timeout=15).run()
        assert not at.exception
        assert "Weather Forecast & Alert Application" in at.title[0].value
        assert any("Search for and select a location" in info.value for info in at.info)

    def test_empty_search_shows_sidebar_warning(self) -> None:
        at = AppTest.from_file(APP_PATH, default_timeout=15).run()
        at.sidebar.text_input[0].input("   ")
        at.sidebar.button[0].click().run()

        assert not at.exception
        assert any("Please enter a city" in w.value for w in at.sidebar.warning)

    @patch("weather_app.services.forecast_service.search_locations")
    def test_location_not_found_shows_warning(self, mock_search: MagicMock) -> None:
        mock_search.side_effect = LocationNotFoundError("No locations found")
        at = AppTest.from_file(APP_PATH, default_timeout=15).run()
        at.sidebar.text_input[0].input("NowhereXYZ")
        at.sidebar.button[0].click().run()

        assert not at.exception
        assert any("No matching locations found" in w.value for w in at.sidebar.warning)

    @patch("weather_app.services.forecast_service.get_weather_dashboard_data")
    @patch("weather_app.services.forecast_service.search_locations")
    def test_successful_search_and_dashboard_render(
        self,
        mock_search: MagicMock,
        mock_get_data: MagicMock,
    ) -> None:
        loc = LocationInfo(
            name="Kolkata",
            latitude=22.56,
            longitude=88.36,
            country="India",
            admin1="West Bengal",
            timezone="Asia/Kolkata",
        )
        mock_search.return_value = [loc]

        mock_client = MagicMock()
        mock_client.fetch_forecast.return_value = _mock_forecast_payload()
        mock_get_data.return_value = get_weather_dashboard_data(
            22.56, 88.36, weather_client=mock_client
        )

        at = AppTest.from_file(APP_PATH, default_timeout=15).run()
        at.sidebar.text_input[0].input("Kolkata")
        at.sidebar.button[0].click().run()

        assert not at.exception
        assert len(at.metric) == 6
        assert any("Current Weather" in sub.value for sub in at.subheader)
        assert any("Weather Visualizations" in sub.value for sub in at.subheader)
        assert any("Weather Advisories" in sub.value for sub in at.subheader)

    @patch("weather_app.services.forecast_service.get_weather_dashboard_data")
    @patch("weather_app.services.forecast_service.search_locations")
    def test_api_timeout_displays_error_gracefully(
        self,
        mock_search: MagicMock,
        mock_get_data: MagicMock,
    ) -> None:
        mock_search.return_value = [
            LocationInfo(name="Kolkata", latitude=22.56, longitude=88.36)
        ]
        mock_get_data.side_effect = APITimeoutError("Request timed out")

        at = AppTest.from_file(APP_PATH, default_timeout=15).run()
        at.sidebar.text_input[0].input("Kolkata")
        at.sidebar.button[0].click().run()

        assert not at.exception
        assert any("Unable to load weather forecast" in err.value for err in at.error)
