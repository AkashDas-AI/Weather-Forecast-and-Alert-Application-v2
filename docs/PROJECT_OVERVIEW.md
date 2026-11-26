# Project Overview: Weather Forecast & Alert Application

**Author:** Akash Das  
**Status:** Phase 11 Implemented (Ready for Phase 12 Deployment)  
**Last Updated:** 2026-11-27

## 1. Purpose
The **Weather Forecast & Alert Application** is a modular Python application that retrieves weather forecasts from Open-Meteo, validates and parses nested JSON into immutable models, computes descriptive forecast statistics, evaluates configurable educational alert thresholds, generates plain-language insights, visualizes trends with Plotly, and exports structured reports (CSV, JSON, Markdown) via a Streamlit dashboard and CLI.

## 2. Problem Statement
Raw meteorological API payloads are nested JSON structures with parallel arrays and numeric WMO codes that are difficult for end users to interpret directly. This project transforms raw forecast responses into validated domain models, visual charts, educational advisories, beginner-friendly explanations, and portable reports.

## 3. Key Features Implemented
- **Open-Meteo & GeoNames Integration:** Geocoding city search and 7-day forecast retrieval (`api/client.py`, `api/geocoding.py`) with timeout/connection/HTTP error translation (`api/_http.py`).
- **Strict Parsing & Domain Models:** Frozen Python 3.11 dataclasses (`models/weather.py`) and validation (`services/weather_service.py`).
- **Descriptive Forecast Analysis:** Temperature, humidity, precipitation (amounts in `mm` separated from probability `%`), wind summaries, and WMO weather code descriptions (`analysis/forecast_analysis.py`).
- **Educational Alert Engine:** Configurable thresholds (`alerts/thresholds.py`) and deduplicated advisories (`alerts/alert_engine.py`) with explicit non-official-warning disclaimers.
- **Interactive Plotly Visualizations:** Six reusable chart builders (`visualization/charts.py`) preserving `None` gaps and local timestamps.
- **Streamlit Dashboard:** Explicit-fetch dashboard (`app.py`) with location search, metrics, tables, charts, advisories, insights, and offline download buttons.
- **Deterministic Insights & Report Exports:** Rule-based interpretation (`analysis/insights.py`), CSV/JSON/Markdown exporters (`reporting/export.py`), and CLI workflow (`scripts/generate_report.py`).
- **Offline Test Suite:** 136 automated `pytest` tests covering all layers offline.

## 4. Documentation Index
See [README.md](./README.md) in `docs/` for the full documentation index.
