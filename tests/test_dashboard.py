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
from weather_app.analysis import WeatherInsights
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
        assert isinstance(bundle.insights, WeatherInsights)
        assert bundle.insights.overview


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
    def test_search_and_selection_do_not_auto_fetch(
        self,
        mock_search: MagicMock,
        mock_get_data: MagicMock,
    ) -> None:
        loc1 = LocationInfo(name="Kolkata", latitude=22.56, longitude=88.36, country="India")
        loc2 = LocationInfo(name="Kolkata North", latitude=22.65, longitude=88.40, country="India")
        mock_search.return_value = [loc1, loc2]

        at = AppTest.from_file(APP_PATH, default_timeout=15).run()
        at.sidebar.text_input[0].input("Kolkata")
        at.sidebar.button[0].click().run()

        assert not at.exception
        mock_get_data.assert_not_called()
        assert len(at.metric) == 0
        assert any("Click **Fetch Forecast**" in info.value for info in at.info)

        # Selecting a different matching location must also not auto-fetch
        at.sidebar.selectbox[0].select_index(1).run()
        assert not at.exception
        mock_get_data.assert_not_called()
        assert len(at.metric) == 0

    @patch("weather_app.services.forecast_service.get_weather_dashboard_data")
    @patch("weather_app.services.forecast_service.search_locations")
    def test_explicit_fetch_reruns_refresh_and_location_switch(
        self,
        mock_search: MagicMock,
        mock_get_data: MagicMock,
    ) -> None:
        loc1 = LocationInfo(
            name="Kolkata",
            latitude=22.56,
            longitude=88.36,
            country="India",
            admin1="West Bengal",
            timezone="Asia/Kolkata",
        )
        loc2 = LocationInfo(
            name="London",
            latitude=51.51,
            longitude=-0.13,
            country="United Kingdom",
            timezone="Europe/London",
        )
        mock_search.return_value = [loc1, loc2]

        mock_client = MagicMock()
        mock_client.fetch_forecast.return_value = _mock_forecast_payload()
        bundle = get_weather_dashboard_data(22.56, 88.36, weather_client=mock_client)
        mock_get_data.return_value = bundle

        at = AppTest.from_file(APP_PATH, default_timeout=15).run()
        at.sidebar.text_input[0].input("Kolkata")
        at.sidebar.button[0].click().run()
        mock_get_data.assert_not_called()

        # Click "Fetch Forecast" (second sidebar button) -> fetches once
        at.sidebar.button[1].click().run()
        assert not at.exception
        assert mock_get_data.call_count == 1
        assert len(at.metric) == 6
        assert any("Current Weather" in sub.value for sub in at.subheader)
        assert any("Weather Visualizations" in sub.value for sub in at.subheader)
        assert any("Weather Advisories" in sub.value for sub in at.subheader)
        assert any("Weather Insights & Interpretation" in sub.value for sub in at.subheader)

        # Ordinary rerun must NOT repeat the fetch
        at.run()
        assert not at.exception
        assert mock_get_data.call_count == 1

        # Clicking "Fetch Forecast" again for the same location requests fresh data
        at.sidebar.button[1].click().run()
        assert not at.exception
        assert mock_get_data.call_count == 2

        # Switching selected location invalidates previous forecast and does not auto-fetch
        at.sidebar.selectbox[0].select_index(1).run()
        assert not at.exception
        assert mock_get_data.call_count == 2
        assert len(at.metric) == 0

        # Failed fetch for the newly selected location shows error and does not show previous forecast
        mock_get_data.side_effect = APITimeoutError("Request timed out")
        at.sidebar.button[1].click().run()
        assert not at.exception
        assert mock_get_data.call_count == 3
        assert len(at.metric) == 0
        assert any("Unable to load weather forecast" in err.value for err in at.error)
