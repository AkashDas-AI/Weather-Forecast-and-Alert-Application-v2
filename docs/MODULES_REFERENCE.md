# Modules Reference

> **Status:** Phase 11 Implemented (Report Generation & Testing Complete; Phase 12 Deployment Pending)  
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
- `src/weather_app/services/`: `parse_forecast_response()` and `parse_geocoding_response()` (`weather_service.py`, Phase 5); `search_locations()`, `get_weather_dashboard_data()`, and `DashboardWeatherBundle` (`forecast_service.py`, Phase 9).
- `src/weather_app/analysis/`: `analyze_forecast()`, `describe_weather_code()`, `WMO_WEATHER_CODES`, `HourlyConditionSummary`, and `ForecastAnalysis` (`forecast_analysis.py`, Phase 6); `generate_weather_insights()` and `WeatherInsights` (`insights.py`, Phase 10).
- `src/weather_app/alerts/`: `AlertThresholds` (`thresholds.py`), `WeatherAlert`, `AlertEvaluation`, `AlertCategory`, `AlertSeverity`, `AlertScope`, and `evaluate_alerts()` (`alert_engine.py`) — Implemented in Phase 7 (educational advisories only).
- `src/weather_app/visualization/`: Reusable Plotly chart builders (`create_hourly_temperature_chart`, `create_daily_temperature_chart`, `create_precipitation_chart`, `create_humidity_chart`, `create_wind_chart`, `create_weather_conditions_chart`) in `charts.py` — Implemented in Phase 8 (Streamlit-independent).
- `src/weather_app/storage/`: SQLite persistence layer.
- `src/weather_app/reporting/`: CSV (`generate_forecast_csv`), JSON (`generate_report_json`, `build_report_payload`), and Markdown (`generate_human_report`) report exporters, safe path/filename utilities (`build_safe_filename`, `resolve_safe_output_path`, `write_report_file`, `export_weather_report`), and `ReportFormat` (`export.py`, `__init__.py`) — Implemented in Phase 11.
- `src/weather_app/utils/`: `parse_iso_datetime()` and `parse_iso_date()` (`date_time.py`) — Implemented in Phase 5.
