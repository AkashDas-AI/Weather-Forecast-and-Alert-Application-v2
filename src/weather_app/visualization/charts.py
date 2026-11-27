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


def _normalize_chart_theme(theme: str) -> str:
    """Validate and normalize chart theme name to 'dark' or 'light'."""
    if not isinstance(theme, str):
        raise ValueError("theme must be 'dark' or 'light'.")
    normalized = theme.strip().lower()
    if normalized not in {"dark", "light"}:
        raise ValueError(f"Unsupported chart theme {theme!r}. Expected 'dark' or 'light'.")
    return normalized


def _apply_chart_theme(fig: go.Figure, theme: str = "light") -> go.Figure:
    """Apply consistent Dark or Light Mode Plotly template and layout colors."""
    mode = _normalize_chart_theme(theme)
    if mode == "dark":
        template = "plotly_dark"
        paper_bg = "#152238"
        plot_bg = "#0f172a"
        font_color = "#f1f5f9"
        grid_color = "#263854"
        axis_line_color = "#334155"
        legend_bg = "rgba(15, 23, 42, 0.75)"
        hover_bg = "#1e293b"
    else:
        template = "plotly_white"
        paper_bg = "#ffffff"
        plot_bg = "#ffffff"
        font_color = "#0f172a"
        grid_color = "#e2e8f0"
        axis_line_color = "#cbd5e1"
        legend_bg = "rgba(255, 255, 255, 0.85)"
        hover_bg = "#f8fafc"

    fig.update_layout(
        template=template,
        paper_bgcolor=paper_bg,
        plot_bgcolor=plot_bg,
        font={"color": font_color},
        title={"font": {"color": font_color}},
        legend={"bgcolor": legend_bg, "font": {"color": font_color}},
        hoverlabel={"bgcolor": hover_bg, "font": {"color": font_color}},
    )
    fig.update_xaxes(
        gridcolor=grid_color,
        linecolor=axis_line_color,
        tickfont={"color": font_color},
        title_font={"color": font_color},
    )
    fig.update_yaxes(
        gridcolor=grid_color,
        linecolor=axis_line_color,
        tickfont={"color": font_color},
        title_font={"color": font_color},
    )
    return fig


def _empty_figure(
    title: str,
    message: str,
    x_title: str = "",
    y_title: str = "",
    theme: str = "light",
) -> go.Figure:
    """Create a clean Plotly figure with an informative empty-state annotation."""
    mode = _normalize_chart_theme(theme)
    text_color = "#f1f5f9" if mode == "dark" else "#0f172a"
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font={"size": 14, "color": text_color},
    )
    fig.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title=y_title,
    )
    return _apply_chart_theme(fig, theme=mode)


def create_hourly_temperature_chart(
    forecast: WeatherForecast,
    title: str | None = None,
    theme: str = "light",
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
            theme=theme,
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
                line={"color": "#38bdf8" if _normalize_chart_theme(theme) == "dark" else "#2563eb"},
                hovertemplate="%{x}<br>Temperature: %{y:.1f} °C<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        title=chart_title,
        xaxis_title=f"Local Time ({forecast.metadata.timezone})",
        yaxis_title="Temperature (°C)",
        hovermode="x unified",
    )
    return _apply_chart_theme(fig, theme=theme)


def create_daily_temperature_chart(
    analysis: ForecastAnalysis,
    title: str | None = None,
    theme: str = "light",
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
            theme=theme,
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
                line={"color": "#f97316"},
                hovertemplate="%{x}<br>Max: %{y:.1f} °C<extra></extra>",
            ),
            go.Scatter(
                x=dates,
                y=t_min,
                mode="lines+markers",
                name="Min Temperature (°C)",
                line={"color": "#38bdf8" if _normalize_chart_theme(theme) == "dark" else "#2563eb"},
                hovertemplate="%{x}<br>Min: %{y:.1f} °C<extra></extra>",
            ),
        ]
    )
    fig.update_layout(
        title=chart_title,
        xaxis_title=f"Local Date ({analysis.timezone})",
        yaxis_title="Temperature (°C)",
        hovermode="x unified",
    )
    return _apply_chart_theme(fig, theme=theme)


def create_precipitation_chart(
    forecast: WeatherForecast,
    title: str | None = None,
    theme: str = "light",
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
            theme=theme,
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
            theme=theme,
        )

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if any(v is not None for v in amounts):
        fig.add_trace(
            go.Bar(
                x=times,
                y=amounts,
                name="Precipitation Amount (mm)",
                marker_color="#38bdf8" if _normalize_chart_theme(theme) == "dark" else "#2563eb",
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
                line={"color": "#f97316"},
                connectgaps=False,
                hovertemplate="%{x}<br>Probability: %{y:.0f}%<extra></extra>",
            ),
            secondary_y=True,
        )

    fig.update_layout(
        title=chart_title,
        xaxis_title=f"Local Time ({forecast.metadata.timezone})",
        hovermode="x unified",
    )
    fig.update_yaxes(title_text="Precipitation Amount (mm)", secondary_y=False)
    fig.update_yaxes(
        title_text="Precipitation Probability (%)",
        range=[0, 100],
        secondary_y=True,
    )
    return _apply_chart_theme(fig, theme=theme)


def create_humidity_chart(
    forecast: WeatherForecast,
    title: str | None = None,
    theme: str = "light",
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
            theme=theme,
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
                line={"color": "#2dd4bf" if _normalize_chart_theme(theme) == "dark" else "#0d9488"},
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
        hovermode="x unified",
    )
    return _apply_chart_theme(fig, theme=theme)


def create_wind_chart(
    forecast: WeatherForecast,
    title: str | None = None,
    theme: str = "light",
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
            theme=theme,
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
                line={"color": "#a78bfa" if _normalize_chart_theme(theme) == "dark" else "#7c3aed"},
                connectgaps=False,
                hovertemplate="%{x}<br>Wind Speed: %{y:.1f} km/h<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        title=chart_title,
        xaxis_title=f"Local Time ({forecast.metadata.timezone})",
        yaxis_title="Wind Speed (km/h)",
        hovermode="x unified",
    )
    return _apply_chart_theme(fig, theme=theme)


def create_weather_conditions_chart(
    analysis: ForecastAnalysis,
    title: str | None = None,
    theme: str = "light",
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
            theme=theme,
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
                marker={"color": "#fbbf24" if _normalize_chart_theme(theme) == "dark" else "#d97706"},
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
    )
    return _apply_chart_theme(fig, theme=theme)
