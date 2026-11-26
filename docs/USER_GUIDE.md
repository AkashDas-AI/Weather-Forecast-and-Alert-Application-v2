# User Guide

**Author:** Akash Das  
**Status:** Phase 11 Implemented (Interactive Streamlit dashboard, insights, and CSV/JSON/Markdown report exports ready)  
**Last Updated:** 2026-11-27

## 1. Application Purpose
The **Weather Forecast & Alert Application** retrieves weather forecasts from Open-Meteo, analyzes meteorological trends, evaluates configurable educational thresholds, and displays charts and advisories in an interactive Streamlit dashboard.

## 2. Installation Prerequisites
- **Python:** 3.11 or later (verified: Python 3.11.0 in `.venv/`)
- **Virtual Environment:** Activate `.venv` in the project root:
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
- **Dependencies:** Declared in `requirements.txt` and `pyproject.toml`.

## 3. Launching & Using the Streamlit Dashboard
1. **Launch the dashboard** from the project root:
   ```powershell
   .venv\Scripts\python.exe -m streamlit run app.py
   ```
2. **Search & Select a Location:** Enter a city or location name in the sidebar search box and click **Search Location**. Choose the matching location from the dropdown list.
3. **Inspect Current Weather & Forecasts:** View current metrics (°C, %, mm, km/h, degrees) and switch between **Daily Forecast** and **Hourly Forecast** tables using local timestamps.
4. **Explore Visualizations:** Inspect the six interactive Plotly charts (hourly temperature, daily temperature range, precipitation & probability, humidity, wind speed, and weather conditions).
5. **Review Educational Advisories:** View any triggered threshold advisories (`info`, `advisory`, `warning`). *Note: These are educational advisories, not official meteorological warnings.*
6. **Read Weather Insights & Interpretation:** Review the plain-language overview, temperature patterns, precipitation outlook, humidity/wind notes, condition transitions, and advisory explanations.
7. **Export Reports:** In the **Export Report** section, download **Hourly CSV**, **Daily CSV**, **JSON**, or **Markdown (MD)** reports directly from the cached dashboard state without triggering extra API requests.
8. **Error Handling:** Empty searches, unknown locations, API timeouts, connection errors, and malformed responses display clear feedback messages without crashing the dashboard.

## 4. Command-Line Report Generation (Phase 11)
Generate reports offline-safe from the CLI (`outputs/exports/` by default):
```powershell
.venv\Scripts\python.exe scripts/generate_report.py --city "Kolkata" --format all
.venv\Scripts\python.exe scripts/generate_report.py --lat 22.5626 --lon 88.3630 --format csv --series daily
```
Supported formats:
- **CSV (`csv`):** Hourly or daily forecast series with units in headers, UTF-8 with BOM (`utf-8-sig`) for spreadsheet compatibility, and empty cells for missing measurements.
- **JSON (`json`):** Structured forecast, analysis, advisories, and insights with ISO-8601 local timestamps and `null` for missing measurements (no API keys or secrets).
- **Markdown (`md`):** Human-readable report separating observed/forecast data from application-generated educational advisories and insights.

**Limitations:** Missing measurements remain `Unavailable` / empty / `null` and are never substituted with `0`. Educational advisories and generated insights are not official meteorological warnings.

## 5. Common Questions
- **Do I need an API key?** No for standard educational/non-commercial usage; Open-Meteo is public and subject to Open-Meteo's [terms](https://open-meteo.com/en/terms).
- **Where are my local settings stored?** Copy `.env.example` to `.env` for local overrides (never commit `.env`).

## 6. Data Attribution
- **Weather Forecast Data:** Provided by **Open-Meteo** under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** licence ([open-meteo.com/en/license](https://open-meteo.com/en/license)). Modifications or derived advisories are indicated by the application.
- **Geocoding Location Data:** Sourced from **GeoNames** via the Open-Meteo Geocoding API ([open-meteo.com/en/docs/geocoding-api](https://open-meteo.com/en/docs/geocoding-api)).
