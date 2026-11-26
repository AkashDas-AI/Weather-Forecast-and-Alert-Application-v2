# User Guide

**Author:** Akash Das  
**Status:** Phase 2 (Application features are planned for Phases 3–11)  
**Last Updated:** 2026-11-27

## 1. Application Purpose
The **Weather Forecast & Alert Application** retrieves weather forecasts, highlights trends, and generates educational rule-based advisories in a Streamlit dashboard.

## 2. Installation Prerequisites
- **Python:** 3.11 or later (verified: Python 3.11.0 in `.venv/`)
- **Virtual Environment:** Activate `.venv` in the project root:
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
- **Dependencies:** Will be listed in `requirements.txt` as implementation phases progress.

## 3. Planned Usage Workflow (Phases 9–11)
- **Launching the Dashboard (Planned Phase 9):** `streamlit run app.py`
- **Selecting a Location (Planned Phase 9):** Enter a city or location name in the dashboard sidebar to resolve coordinates and load forecasts.
- **Reading Forecasts (Planned Phases 6 & 8):** View current conditions, hourly/daily metrics, and trend charts.
- **Understanding Alerts (Planned Phase 7):** Advisories are triggered when forecast values cross configurable thresholds (high/low temperature, heavy rainfall probability, high humidity, strong wind). *Note: These are educational advisories, not official emergency warnings.*
- **Exporting Reports (Planned Phase 11):** Export processed forecast summaries to CSV or JSON in `outputs/exports/`.

## 4. Common Questions
- **Do I need an API key?** No for standard usage; the planned primary provider (Open-Meteo) is public.
- **Where are my local settings stored?** Copy `.env.example` to `.env` for local overrides (never commit `.env`).
