"""Reusable Plotly weather visualization functions (Streamlit-independent).

Author: Akash Das
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from weather_app.analysis.forecast_analysis import (
    ForecastAnalysis,
    describe_weather_code,
)
from weather_app.models.weather import WeatherForecast


def _empty_figure(title: str, message: str, x_title: str = "", y_title: str = "") -> go.Figure:
    """Create a clean Plotly figure with an informative empty-state annotation."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font={"size": 14},
    )
    fig.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title=y_title,
        template="plotly_white",
    )
    return fig


def create_hourly_temperature_chart(
    forecast: WeatherForecast,
    title: str | None = None,
) -> go.Figure:
    """Create an hourly temperature trend chart (°C) from a WeatherForecast."""
    if not isinstance(forecast, WeatherForecast):
        raise TypeError("forecast must be a WeatherForecast instance.")

    chart_title = title or f"Hourly Temperature Forecast ({forecast.metadata.timezone})"
    if not forecast.hourly:
        return _empty_figure(
            chart_title,
            "No hourly temperature data available.",
            x_title="Local Time",
            y_title="Temperature (°C)",
        )

    times = [h.time for h in forecast.hourly]
    temps = [h.temperature_2m for h in forecast.hourly]

    fig = go.Figure(
        data=[
            go.Scatter(
                x=times,
                y=temps,
                mode="lines+markers",
                name="Temperature (°C)",
                hovertemplate="%{x}<br>Temperature: %{y:.1f} °C<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        title=chart_title,
        xaxis_title=f"Local Time ({forecast.metadata.timezone})",
        yaxis_title="Temperature (°C)",
        template="plotly_white",
        hovermode="x unified",
    )
    return fig


def create_daily_temperature_chart(
    analysis: ForecastAnalysis,
    title: str | None = None,
) -> go.Figure:
    """Create a daily min/max temperature comparison chart (°C) from ForecastAnalysis."""
    if not isinstance(analysis, ForecastAnalysis):
        raise TypeError("analysis must be a ForecastAnalysis instance.")

    chart_title = title or f"Daily Temperature Range ({analysis.timezone})"
    if not analysis.daily_summaries:
        return _empty_figure(
            chart_title,
            "No daily temperature data available.",
            x_title="Local Date",
            y_title="Temperature (°C)",
        )

    dates = [d.date for d in analysis.daily_summaries]
    t_max = [d.temp_max_c for d in analysis.daily_summaries]
    t_min = [d.temp_min_c for d in analysis.daily_summaries]

    fig = go.Figure(
        data=[
            go.Scatter(
                x=dates,
                y=t_max,
                mode="lines+markers",
                name="Max Temperature (°C)",
                hovertemplate="%{x}<br>Max: %{y:.1f} °C<extra></extra>",
            ),
            go.Scatter(
                x=dates,
                y=t_min,
                mode="lines+markers",
                name="Min Temperature (°C)",
                hovertemplate="%{x}<br>Min: %{y:.1f} °C<extra></extra>",
            ),
        ]
    )
    fig.update_layout(
        title=chart_title,
        xaxis_title=f"Local Date ({analysis.timezone})",
        yaxis_title="Temperature (°C)",
        template="plotly_white",
        hovermode="x unified",
    )
    return fig


def create_precipitation_chart(
    forecast: WeatherForecast,
    title: str | None = None,
) -> go.Figure:
    """Create an hourly precipitation amount (mm) and probability (%) chart."""
    if not isinstance(forecast, WeatherForecast):
        raise TypeError("forecast must be a WeatherForecast instance.")

    chart_title = title or f"Hourly Precipitation & Probability ({forecast.metadata.timezone})"
    if not forecast.hourly:
        return _empty_figure(
            chart_title,
            "No hourly precipitation data available.",
            x_title="Local Time",
            y_title="Precipitation (mm)",
        )

    times = [h.time for h in forecast.hourly]
    amounts = [h.precipitation for h in forecast.hourly]
    probs = [h.precipitation_probability for h in forecast.hourly]

    if all(v is None for v in amounts) and all(v is None for v in probs):
        return _empty_figure(
            chart_title,
            "Precipitation amount and probability data are unavailable.",
            x_title=f"Local Time ({forecast.metadata.timezone})",
            y_title="Precipitation (mm)",
        )

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if any(v is not None for v in amounts):
        fig.add_trace(
            go.Bar(
                x=times,
                y=amounts,
                name="Precipitation Amount (mm)",
                hovertemplate="%{x}<br>Amount: %{y:.2f} mm<extra></extra>",
            ),
            secondary_y=False,
        )
    if any(v is not None for v in probs):
        fig.add_trace(
            go.Scatter(
                x=times,
                y=probs,
                mode="lines+markers",
                name="Precipitation Probability (%)",
                connectgaps=False,
                hovertemplate="%{x}<br>Probability: %{y:.0f}%<extra></extra>",
            ),
            secondary_y=True,
        )

    fig.update_layout(
        title=chart_title,
        xaxis_title=f"Local Time ({forecast.metadata.timezone})",
        template="plotly_white",
        hovermode="x unified",
    )
    fig.update_yaxes(title_text="Precipitation Amount (mm)", secondary_y=False)
    fig.update_yaxes(
        title_text="Precipitation Probability (%)",
        range=[0, 100],
        secondary_y=True,
    )
    return fig


def create_humidity_chart(
    forecast: WeatherForecast,
    title: str | None = None,
) -> go.Figure:
    """Create an hourly relative humidity trend chart (%) from a WeatherForecast."""
    if not isinstance(forecast, WeatherForecast):
        raise TypeError("forecast must be a WeatherForecast instance.")

    chart_title = title or f"Hourly Relative Humidity ({forecast.metadata.timezone})"
    if not forecast.hourly or all(h.relative_humidity_2m is None for h in forecast.hourly):
        return _empty_figure(
            chart_title,
            "No hourly relative humidity data available.",
            x_title=f"Local Time ({forecast.metadata.timezone})",
            y_title="Relative Humidity (%)",
        )

    times = [h.time for h in forecast.hourly]
    humidities = [h.relative_humidity_2m for h in forecast.hourly]

    fig = go.Figure(
        data=[
            go.Scatter(
                x=times,
                y=humidities,
                mode="lines+markers",
                name="Relative Humidity (%)",
                connectgaps=False,
                hovertemplate="%{x}<br>Humidity: %{y:.0f}%<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        title=chart_title,
        xaxis_title=f"Local Time ({forecast.metadata.timezone})",
        yaxis_title="Relative Humidity (%)",
        yaxis={"range": [0, 100]},
        template="plotly_white",
        hovermode="x unified",
    )
    return fig


def create_wind_chart(
    forecast: WeatherForecast,
    title: str | None = None,
) -> go.Figure:
    """Create an hourly wind speed trend chart (km/h) from a WeatherForecast."""
    if not isinstance(forecast, WeatherForecast):
        raise TypeError("forecast must be a WeatherForecast instance.")

    chart_title = title or f"Hourly Wind Speed ({forecast.metadata.timezone})"
    if not forecast.hourly or all(h.wind_speed_10m is None for h in forecast.hourly):
        return _empty_figure(
            chart_title,
            "No hourly wind speed data available.",
            x_title=f"Local Time ({forecast.metadata.timezone})",
            y_title="Wind Speed (km/h)",
        )

    times = [h.time for h in forecast.hourly]
    speeds = [h.wind_speed_10m for h in forecast.hourly]

    fig = go.Figure(
        data=[
            go.Scatter(
                x=times,
                y=speeds,
                mode="lines+markers",
                name="Wind Speed (km/h)",
                connectgaps=False,
                hovertemplate="%{x}<br>Wind Speed: %{y:.1f} km/h<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        title=chart_title,
        xaxis_title=f"Local Time ({forecast.metadata.timezone})",
        yaxis_title="Wind Speed (km/h)",
        template="plotly_white",
        hovermode="x unified",
    )
    return fig


def create_weather_conditions_chart(
    analysis: ForecastAnalysis,
    title: str | None = None,
) -> go.Figure:
    """Create a timeline of forecast weather condition descriptions using WMO codes."""
    if not isinstance(analysis, ForecastAnalysis):
        raise TypeError("analysis must be a ForecastAnalysis instance.")

    chart_title = title or f"Forecast Weather Conditions ({analysis.timezone})"
    if not analysis.hourly_summaries:
        return _empty_figure(
            chart_title,
            "No hourly weather condition data available.",
            x_title=f"Local Time ({analysis.timezone})",
            y_title="Weather Condition",
        )

    times = [h.time for h in analysis.hourly_summaries]
    descriptions = [
        h.condition_description or describe_weather_code(h.weather_code)
        for h in analysis.hourly_summaries
    ]
    temps = [h.temperature_c for h in analysis.hourly_summaries]
    codes = [
        str(h.weather_code) if h.weather_code is not None else "N/A"
        for h in analysis.hourly_summaries
    ]

    fig = go.Figure(
        data=[
            go.Scatter(
                x=times,
                y=descriptions,
                mode="markers+text",
                name="Weather Condition",
                customdata=list(zip(temps, codes)),
                hovertemplate=(
                    "%{x}<br>Condition: %{y}<br>"
                    "Temp: %{customdata[0]:.1f} °C<br>"
                    "WMO Code: %{customdata[1]}<extra></extra>"
                ),
            )
        ]
    )
    fig.update_layout(
        title=chart_title,
        xaxis_title=f"Local Time ({analysis.timezone})",
        yaxis_title="Condition Description",
        template="plotly_white",
    )
    return fig
