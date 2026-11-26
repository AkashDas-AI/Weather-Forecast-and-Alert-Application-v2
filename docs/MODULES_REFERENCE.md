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
- `src/weather_app/api/`: Weather API client and geocoding.
- `src/weather_app/core/`: Centralized configuration and custom exceptions.
- `src/weather_app/models/`: Structured weather data models.
- `src/weather_app/services/`: Weather and forecast orchestration services.
- `src/weather_app/analysis/`: Forecast trend and metric analysis.
- `src/weather_app/alerts/`: Configurable alert rules and thresholds.
- `src/weather_app/visualization/`: Forecast charts and visualizations.
- `src/weather_app/storage/`: SQLite persistence layer.
- `src/weather_app/reporting/`: CSV/JSON report export.
- `src/weather_app/utils/`: Shared date/time and helper utilities.
