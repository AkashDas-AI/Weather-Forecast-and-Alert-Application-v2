"""Streamlit dashboard entry point for the Weather Forecast & Alert Application.

Author: Akash Das
"""

from pathlib import Path
import sys

# Ensure src/ is importable when launched via `streamlit run app.py` from project root
_SRC_DIR = Path(__file__).resolve().parent / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

import streamlit as st

from weather_app.alerts import AlertSeverity
from weather_app.core.exceptions import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    DataParsingError,
    LocationNotFoundError,
    WeatherAppError,
)
from weather_app.models import LocationInfo
from weather_app.services.forecast_service import (
    DashboardWeatherBundle,
    format_location_label,
    get_weather_dashboard_data,
    search_locations,
)
from weather_app.visualization import (
    create_daily_temperature_chart,
    create_humidity_chart,
    create_hourly_temperature_chart,
    create_precipitation_chart,
    create_weather_conditions_chart,
    create_wind_chart,
)


def _format_optional(value: float | int | None, unit: str = "", precision: int = 1) -> str:
    """Format an optional numeric measurement without inventing unavailable values."""
    if value is None:
        return "Unavailable"
    if isinstance(value, int):
        return f"{value}{unit}"
    return f"{value:.{precision}f}{unit}"


def _render_header(bundle: DashboardWeatherBundle | None, location: LocationInfo | None) -> None:
    """Render Section A: Application header."""
    st.title("Weather Forecast & Alert Application")
    st.caption(
        "Interactive weather monitoring, forecast visualization, and educational "
        "rule-based advisories. Weather data: Open-Meteo (CC BY 4.0) | Geocoding: GeoNames."
    )
    if location is not None and bundle is not None:
        st.info(
            f"**Selected Location:** {format_location_label(location)}  |  "
            f"**Local Timezone:** `{bundle.analysis.timezone}`"
        )


def _render_location_search() -> LocationInfo | None:
    """Render Section B: Location search and selection in the sidebar."""
    st.sidebar.header("Location Search")
    with st.sidebar.form("location_search_form"):
        query = st.text_input(
            "City or Location Name",
            placeholder="e.g., Kolkata, London, Tokyo",
        )
        submitted = st.form_submit_button("Search Location")

    if submitted:
        cleaned = query.strip()
        if not cleaned:
            st.sidebar.warning("Please enter a city or location name before searching.")
        else:
            try:
                results = search_locations(cleaned)
                st.session_state["search_results"] = results
                st.session_state["selected_location"] = results[0]
                st.session_state.pop("weather_bundle", None)
                st.session_state["fetch_requested"] = False
            except LocationNotFoundError:
                st.session_state["search_results"] = []
                st.session_state["selected_location"] = None
                st.session_state.pop("weather_bundle", None)
                st.session_state["fetch_requested"] = False
                st.sidebar.warning(f"No matching locations found for '{cleaned}'.")
            except (APITimeoutError, APIConnectionError, APIError, DataParsingError) as exc:
                st.sidebar.error(f"Location search failed: {exc}")
            except Exception:
                st.sidebar.error("An unexpected error occurred while searching for locations.")

    results: list[LocationInfo] = st.session_state.get("search_results", [])
    if not results:
        return None

    labels = [format_location_label(loc) for loc in results]
    selected_idx = st.sidebar.selectbox(
        "Select Matching Location",
        options=range(len(results)),
        format_func=lambda idx: labels[idx],
        key="location_select_index",
    )
    selected_location = results[selected_idx]
    prev_selected: LocationInfo | None = st.session_state.get("selected_location")
    if prev_selected != selected_location:
        st.session_state["selected_location"] = selected_location
        st.session_state.pop("weather_bundle", None)
        st.session_state["fetch_requested"] = False

    if st.sidebar.button("Fetch Forecast", type="primary"):
        st.session_state.pop("weather_bundle", None)
        st.session_state["fetch_requested"] = True

    return selected_location


def _render_current_weather(bundle: DashboardWeatherBundle) -> None:
    """Render Section C: Current weather measurements."""
    st.subheader("Current Weather")
    cur = bundle.analysis.current
    st.markdown(
        f"**Condition:** {cur.condition_description}  |  "
        f"**Observation Time (Local):** `{cur.time.strftime('%Y-%m-%d %H:%M')}`"
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Temperature", _format_optional(cur.temperature_c, " °C"))
    col2.metric("Feels Like", _format_optional(cur.apparent_temperature_c, " °C"))
    col3.metric("Relative Humidity", _format_optional(cur.relative_humidity_pct, " %", 0))
    col4.metric("Precipitation", _format_optional(cur.precipitation_mm, " mm"))

    col5, col6 = st.columns(2)
    col5.metric("Wind Speed", _format_optional(cur.wind_speed_kmh, " km/h"))
    col6.metric("Wind Direction", _format_optional(cur.wind_direction_deg, "°", 0))


def _render_forecasts(bundle: DashboardWeatherBundle) -> None:
    """Render Section D: Hourly and daily forecast tables."""
    st.subheader("Forecast Overview")
    analysis = bundle.analysis

    tab_daily, tab_hourly = st.tabs(["Daily Forecast", "Hourly Forecast"])
    with tab_daily:
        if not analysis.daily_summaries:
            st.info("No daily forecast data available.")
        else:
            daily_rows = [
                {
                    "Local Date": d.date.isoformat(),
                    "Min Temp (°C)": d.temp_min_c,
                    "Max Temp (°C)": d.temp_max_c,
                    "Precip Sum (mm)": d.precipitation_sum_mm,
                    "Max Precip Prob (%)": d.precipitation_probability_max_pct,
                    "Max Wind (km/h)": d.wind_speed_max_kmh,
                    "Condition": d.condition_description,
                }
                for d in analysis.daily_summaries
            ]
            st.dataframe(daily_rows, width="stretch", hide_index=True)

    with tab_hourly:
        if not analysis.hourly_summaries:
            st.info("No hourly forecast data available.")
        else:
            hourly_rows = [
                {
                    "Local Time": h.time.strftime("%Y-%m-%d %H:%M"),
                    "Temp (°C)": h.temperature_c,
                    "Precip (mm)": h.precipitation_mm,
                    "Precip Prob (%)": h.precipitation_probability_pct,
                    "Wind (km/h)": h.wind_speed_kmh,
                    "Condition": h.condition_description,
                }
                for h in analysis.hourly_summaries
            ]
            st.dataframe(hourly_rows, width="stretch", hide_index=True)


def _render_visualizations(bundle: DashboardWeatherBundle) -> None:
    """Render Section E: Phase 8 Plotly visualizations."""
    st.subheader("Weather Visualizations")
    forecast = bundle.forecast
    analysis = bundle.analysis

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(create_hourly_temperature_chart(forecast), width="stretch")
        st.plotly_chart(create_precipitation_chart(forecast), width="stretch")
        st.plotly_chart(create_wind_chart(forecast), width="stretch")
    with col2:
        st.plotly_chart(create_daily_temperature_chart(analysis), width="stretch")
        st.plotly_chart(create_humidity_chart(forecast), width="stretch")
        st.plotly_chart(create_weather_conditions_chart(analysis), width="stretch")


def _render_advisories(bundle: DashboardWeatherBundle) -> None:
    """Render Section F: Phase 7 educational weather advisories."""
    st.subheader("Weather Advisories")
    evaluation = bundle.alert_evaluation
    st.caption(evaluation.disclaimer)

    if evaluation.total_count == 0:
        st.success("No weather advisories triggered for the configured educational thresholds.")
        return

    st.write(f"**{evaluation.total_count}** educational advisory item(s) detected:")
    for alert in evaluation.alerts:
        label = (
            f"[{alert.severity.value.upper()}] {alert.title} — "
            f"{alert.scope.value.capitalize()} ({alert.timestamp.isoformat()})"
        )
        body = (
            f"- **Category:** `{alert.category.value}`\n"
            f"- **Severity:** `{alert.severity.value}`\n"
            f"- **Scope:** `{alert.scope.value}`\n"
            f"- **Time (Local):** `{alert.timestamp.isoformat()}`\n"
            f"- **Measured:** `{alert.measured_value} {alert.unit}` "
            f"(Threshold: `{alert.threshold_context}`)\n"
            f"- **Explanation:** {alert.description}"
        )
        if alert.severity == AlertSeverity.WARNING:
            st.error(f"**{label}**\n\n{body}")
        elif alert.severity == AlertSeverity.ADVISORY:
            st.warning(f"**{label}**\n\n{body}")
        else:
            st.info(f"**{label}**\n\n{body}")


def main() -> None:
    """Run the Streamlit weather forecast and alert dashboard."""
    st.set_page_config(
        page_title="Weather Forecast & Alert Application",
        layout="wide",
    )

    selected_location = _render_location_search()
    bundle: DashboardWeatherBundle | None = st.session_state.get("weather_bundle")
    fetch_requested: bool = st.session_state.get("fetch_requested", False)
    fetch_failed = False

    if selected_location is not None and fetch_requested and bundle is None:
        with st.spinner("Fetching and analyzing forecast data..."):
            try:
                bundle = get_weather_dashboard_data(
                    latitude=selected_location.latitude,
                    longitude=selected_location.longitude,
                )
                st.session_state["weather_bundle"] = bundle
            except (APITimeoutError, APIConnectionError, APIError, DataParsingError, WeatherAppError) as exc:
                st.session_state.pop("weather_bundle", None)
                fetch_failed = True
                st.error(f"Unable to load weather forecast: {exc}")
            except Exception:
                st.session_state.pop("weather_bundle", None)
                fetch_failed = True
                st.error("An unexpected error occurred while loading weather data.")
            finally:
                st.session_state["fetch_requested"] = False

    _render_header(bundle, selected_location)

    if selected_location is None:
        st.info("Search for and select a location in the sidebar to view its weather forecast.")
        return

    if bundle is None:
        if not fetch_failed:
            st.info("Click **Fetch Forecast** in the sidebar to load weather data for the selected location.")
        return

    _render_current_weather(bundle)
    st.divider()
    _render_forecasts(bundle)
    st.divider()
    _render_visualizations(bundle)
    st.divider()
    _render_advisories(bundle)


if __name__ == "__main__":
    main()
