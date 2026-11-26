"""Dashboard orchestration service connecting API clients, parsing, analysis, and alerts.

Author: Akash Das
"""

from dataclasses import dataclass

from weather_app.alerts import AlertEvaluation, AlertThresholds, evaluate_alerts
from weather_app.analysis import ForecastAnalysis, analyze_forecast
from weather_app.api.client import WeatherAPIClient
from weather_app.api.geocoding import GeocodingClient
from weather_app.models import LocationInfo, WeatherForecast
from weather_app.services.weather_service import (
    parse_forecast_response,
    parse_geocoding_response,
)


@dataclass(frozen=True)
class DashboardWeatherBundle:
    """Aggregated forecast, analysis, and advisory evaluation for dashboard rendering."""

    forecast: WeatherForecast
    analysis: ForecastAnalysis
    alert_evaluation: AlertEvaluation


def format_location_label(location: LocationInfo) -> str:
    """Format a LocationInfo into a readable label for selection widgets."""
    parts = [location.name]
    if location.admin1:
        parts.append(location.admin1)
    if location.country:
        parts.append(location.country)
    return f"{', '.join(parts)} ({location.latitude:.2f}, {location.longitude:.2f})"


def search_locations(
    query: str,
    geocoding_client: GeocodingClient | None = None,
) -> list[LocationInfo]:
    """Search matching locations for a city/place query and return LocationInfo records."""
    client = geocoding_client or GeocodingClient()
    raw_payload = client.search_location(query)
    return parse_geocoding_response(raw_payload)


def get_weather_dashboard_data(
    latitude: float,
    longitude: float,
    weather_client: WeatherAPIClient | None = None,
    thresholds: AlertThresholds | None = None,
) -> DashboardWeatherBundle:
    """Fetch, parse, analyze, and evaluate alerts for the given coordinates."""
    client = weather_client or WeatherAPIClient()
    raw_forecast = client.fetch_forecast(latitude=latitude, longitude=longitude)
    forecast = parse_forecast_response(raw_forecast)
    analysis = analyze_forecast(forecast)
    alert_evaluation = evaluate_alerts(analysis, thresholds=thresholds)
    return DashboardWeatherBundle(
        forecast=forecast,
        analysis=analysis,
        alert_evaluation=alert_evaluation,
    )
