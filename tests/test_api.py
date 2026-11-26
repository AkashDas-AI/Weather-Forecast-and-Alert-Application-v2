"""Unit tests for WeatherAPIClient and GeocodingClient (Phase 4).

All HTTP calls are mocked; tests do not require live internet or API access.
"""

from unittest.mock import MagicMock, patch

import pytest
import requests

from weather_app.api.client import WeatherAPIClient
from weather_app.api.geocoding import GeocodingClient
from weather_app.core.config import APIConfig
from weather_app.core.exceptions import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    LocationNotFoundError,
)


def _mock_response(payload=None, status_code: int = 200, json_error: bool = False):
    """Create a mock requests.Response object."""
    resp = MagicMock()
    resp.status_code = status_code
    if status_code >= 400:
        http_err = requests.exceptions.HTTPError(f"HTTP {status_code}", response=resp)
        resp.raise_for_status.side_effect = http_err
    else:
        resp.raise_for_status.return_value = None

    if json_error:
        resp.json.side_effect = ValueError("Invalid JSON")
    else:
        resp.json.return_value = payload
    return resp


class TestWeatherAPIClient:
    """Tests for WeatherAPIClient.fetch_forecast."""

    @patch("weather_app.api._http.requests.get")
    def test_fetch_forecast_success_and_request_args(self, mock_get: MagicMock) -> None:
        sample_payload = {"latitude": 51.5, "longitude": -0.12, "current": {"temperature_2m": 15.0}}
        mock_get.return_value = _mock_response(payload=sample_payload)

        cfg = APIConfig(timeout_seconds=12)
        client = WeatherAPIClient(cfg)
        result = client.fetch_forecast(latitude=51.5, longitude=-0.12)

        assert result == sample_payload
        mock_get.assert_called_once()
        call_args, call_kwargs = mock_get.call_args
        assert call_args[0] == "https://api.open-meteo.com/v1/forecast"
        assert call_kwargs["timeout"] == 12
        assert call_kwargs["params"]["latitude"] == 51.5
        assert call_kwargs["params"]["longitude"] == -0.12
        assert call_kwargs["params"]["forecast_days"] == 7
        assert call_kwargs["params"]["timezone"] == "auto"

    @patch("weather_app.api._http.requests.get")
    def test_fetch_forecast_http_error(self, mock_get: MagicMock) -> None:
        mock_get.return_value = _mock_response(status_code=503)
        client = WeatherAPIClient()

        with pytest.raises(APIError) as exc_info:
            client.fetch_forecast(51.5, -0.12)
        assert exc_info.value.status_code == 503

    @patch("weather_app.api._http.requests.get")
    def test_fetch_forecast_timeout(self, mock_get: MagicMock) -> None:
        mock_get.side_effect = requests.exceptions.Timeout("Timed out")
        client = WeatherAPIClient()

        with pytest.raises(APITimeoutError):
            client.fetch_forecast(51.5, -0.12)

    @patch("weather_app.api._http.requests.get")
    def test_fetch_forecast_connection_error(self, mock_get: MagicMock) -> None:
        mock_get.side_effect = requests.exceptions.ConnectionError("DNS failed")
        client = WeatherAPIClient()

        with pytest.raises(APIConnectionError):
            client.fetch_forecast(51.5, -0.12)

    @patch("weather_app.api._http.requests.get")
    def test_fetch_forecast_malformed_json(self, mock_get: MagicMock) -> None:
        mock_get.return_value = _mock_response(json_error=True)
        client = WeatherAPIClient()

        with pytest.raises(APIError, match="Malformed JSON"):
            client.fetch_forecast(51.5, -0.12)

    @patch("weather_app.api._http.requests.get")
    def test_fetch_forecast_non_dict_json(self, mock_get: MagicMock) -> None:
        mock_get.return_value = _mock_response(payload=[1, 2, 3])
        client = WeatherAPIClient()

        with pytest.raises(APIError, match="expected object"):
            client.fetch_forecast(51.5, -0.12)

    @pytest.mark.parametrize(
        "lat,lon,days",
        [
            (-91.0, 0.0, 7),
            (91.0, 0.0, 7),
            (0.0, -181.0, 7),
            (0.0, 181.0, 7),
            (True, 0.0, 7),
            (0.0, 0.0, 0),
            (0.0, 0.0, 17),
            (0.0, 0.0, True),
        ],
    )
    def test_fetch_forecast_invalid_inputs(self, lat, lon, days) -> None:
        client = WeatherAPIClient()
        with pytest.raises(ValueError):
            client.fetch_forecast(lat, lon, forecast_days=days)


class TestGeocodingClient:
    """Tests for GeocodingClient.search_location."""

    @patch("weather_app.api._http.requests.get")
    def test_search_location_success_and_request_args(self, mock_get: MagicMock) -> None:
        sample_payload = {
            "results": [
                {"id": 1, "name": "London", "latitude": 51.5085, "longitude": -0.1257}
            ]
        }
        mock_get.return_value = _mock_response(payload=sample_payload)

        cfg = APIConfig(timeout_seconds=8)
        client = GeocodingClient(cfg)
        result = client.search_location("  London  ", count=3, language="en")

        assert result == sample_payload
        mock_get.assert_called_once()
        call_args, call_kwargs = mock_get.call_args
        assert call_args[0] == "https://geocoding-api.open-meteo.com/v1/search"
        assert call_kwargs["timeout"] == 8
        assert call_kwargs["params"] == {
            "name": "London",
            "count": 3,
            "language": "en",
            "format": "json",
        }

    @patch("weather_app.api._http.requests.get")
    def test_search_location_empty_results_raises_not_found(self, mock_get: MagicMock) -> None:
        mock_get.return_value = _mock_response(payload={"generationtime_ms": 0.4})
        client = GeocodingClient()

        with pytest.raises(LocationNotFoundError):
            client.search_location("NonExistentCityXYZ")

    @patch("weather_app.api._http.requests.get")
    def test_search_location_http_error(self, mock_get: MagicMock) -> None:
        mock_get.return_value = _mock_response(status_code=500)
        client = GeocodingClient()

        with pytest.raises(APIError) as exc_info:
            client.search_location("London")
        assert exc_info.value.status_code == 500

    @patch("weather_app.api._http.requests.get")
    def test_search_location_timeout(self, mock_get: MagicMock) -> None:
        mock_get.side_effect = requests.exceptions.Timeout("Timed out")
        client = GeocodingClient()

        with pytest.raises(APITimeoutError):
            client.search_location("London")

    @patch("weather_app.api._http.requests.get")
    def test_search_location_connection_error(self, mock_get: MagicMock) -> None:
        mock_get.side_effect = requests.exceptions.ConnectionError("Offline")
        client = GeocodingClient()

        with pytest.raises(APIConnectionError):
            client.search_location("London")

    @patch("weather_app.api._http.requests.get")
    def test_search_location_malformed_json(self, mock_get: MagicMock) -> None:
        mock_get.return_value = _mock_response(json_error=True)
        client = GeocodingClient()

        with pytest.raises(APIError, match="Malformed JSON"):
            client.search_location("London")

    @pytest.mark.parametrize(
        "query,count",
        [
            ("", 5),
            ("   ", 5),
            (None, 5),
            ("London", 0),
            ("London", 101),
            ("London", True),
        ],
    )
    def test_search_location_invalid_inputs(self, query, count) -> None:
        client = GeocodingClient()
        with pytest.raises(ValueError):
            client.search_location(query, count=count)
