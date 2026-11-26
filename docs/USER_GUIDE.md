# User Guide

**Author:** Akash Das  
**Status:** Phase 9 Implemented (Interactive Streamlit dashboard ready; insights & exports planned for Phases 10–11)  
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
6. **Error Handling:** Empty searches, unknown locations, API timeouts, connection errors, and malformed responses display clear feedback messages without crashing the dashboard.

## 4. Planned Features (Phases 10–11)
- **Weather Insights (Phase 10):** Plain-language forecast interpretation summaries.
- **Report Exports (Phase 11):** CSV/JSON report export into `outputs/exports/`.

## 5. Common Questions
- **Do I need an API key?** No for standard educational/non-commercial usage; Open-Meteo is public and subject to Open-Meteo's [terms](https://open-meteo.com/en/terms).
- **Where are my local settings stored?** Copy `.env.example` to `.env` for local overrides (never commit `.env`).

## 6. Data Attribution
- **Weather Forecast Data:** Provided by **Open-Meteo** under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** licence ([open-meteo.com/en/license](https://open-meteo.com/en/license)). Modifications or derived advisories are indicated by the application.
- **Geocoding Location Data:** Sourced from **GeoNames** via the Open-Meteo Geocoding API ([open-meteo.com/en/docs/geocoding-api](https://open-meteo.com/en/docs/geocoding-api)).
