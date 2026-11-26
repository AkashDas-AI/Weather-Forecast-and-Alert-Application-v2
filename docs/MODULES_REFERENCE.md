# Modules Reference

> **Status:** Phase 2 Scaffolded (Awaiting Implementation in Phases 3–11)  
> **Last Updated:** 2026-11-27

## 1. Repository Structure

```text
Weather Forecast & Alert Application System/
├── .github/workflows/tests.yml
├── .streamlit/config.toml
├── data/
│   ├── sample/sample_weather.json
│   └── README.md
├── docs/
├── images/{screenshots,diagrams}/
├── outputs/{charts,exports,logs}/
├── reports/README.md
├── scripts/{run_monitor.py,generate_report.py}
├── src/weather_app/
│   ├── api/{client.py,geocoding.py}
│   ├── core/{config.py,exceptions.py}
│   ├── models/weather.py
│   ├── services/{weather_service.py,forecast_service.py}
│   ├── analysis/forecast_analysis.py
│   ├── alerts/{alert_engine.py,thresholds.py}
│   ├── visualization/charts.py
│   ├── storage/database.py
│   ├── reporting/export.py
│   └── utils/date_time.py
├── tests/{conftest.py,test_api.py,test_analysis.py,test_alerts.py,test_reporting.py}
├── .env.example
├── .editorconfig
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── app.py
├── main.py
├── pyproject.toml
└── requirements.txt
```

## 2. Package Responsibilities
- `src/weather_app/api/`: `WeatherAPIClient` (`client.py`) and `GeocodingClient` (`geocoding.py`) — Phase 3 parameter builders and interfaces ready; live HTTP fetching planned for Phase 4.
- `src/weather_app/core/`: `APIConfig` and `get_api_config()` (`config.py`), plus `WeatherAppError` hierarchy (`exceptions.py`) — Configured in Phase 3.
- `src/weather_app/models/`: `LocationInfo`, `ForecastMetadata`, `CurrentWeather`, `HourlyForecast`, `DailyForecast`, `WeatherForecast` (`weather.py`) — Implemented in Phase 5.
- `src/weather_app/services/`: `parse_forecast_response()` and `parse_geocoding_response()` (`weather_service.py`) — Implemented in Phase 5; `forecast_service.py` planned for later phases.
- `src/weather_app/analysis/`: `analyze_forecast()`, `describe_weather_code()`, `WMO_WEATHER_CODES`, `HourlyConditionSummary`, and `ForecastAnalysis` result models (`forecast_analysis.py`) — Implemented in Phase 6 (descriptive summaries only; alert classification deferred to Phase 7).
- `src/weather_app/alerts/`: Configurable alert rules and thresholds.
- `src/weather_app/visualization/`: Forecast charts and visualizations.
- `src/weather_app/storage/`: SQLite persistence layer.
- `src/weather_app/reporting/`: CSV/JSON report export.
- `src/weather_app/utils/`: `parse_iso_datetime()` and `parse_iso_date()` (`date_time.py`) — Implemented in Phase 5.
