# Project Overview: Weather Forecast & Alert Application

**Author:** Akash Das  
**Status:** Phase 2 (Folder Structure & Documentation Cleanup)  
**Last Updated:** 2026-11-27

## 1. Purpose
The **Weather Forecast & Alert Application** is a modular Python application that retrieves weather data from a public weather API, parses and analyzes forecast trends, evaluates configurable advisory thresholds, and presents insights and visualizations through an interactive Streamlit dashboard.

## 2. Problem Statement
Raw meteorological API payloads are nested JSON structures that are difficult for end users to interpret directly. This project transforms raw forecast data into structured analytics, visual charts, and clear rule-based advisories in one cohesive interface.

## 3. Objectives
- Integrate with a public weather API (planned: Open-Meteo) with geocoding support.
- Parse and validate current, hourly, and daily weather responses safely.
- Analyze forecast trends (temperature, precipitation probability, humidity, wind) using Pandas.
- Generate configurable, educational weather advisories (not official emergency warnings).
- Present forecasts, charts, insights, and CSV/JSON exports in an interactive Streamlit dashboard.

## 4. Intended Users
- Students and junior developers reviewing portfolio-grade Python architecture.
- General users who want a clean, configurable weather forecast and advisory dashboard.

## 5. Main Features (Planned vs. Implemented)
- **Implemented:** Isolated Python 3.11 `.venv`, modular `src/weather_app/` package scaffold, test scaffold, sample JSON dataset, and project documentation.
- **Planned (Phases 3–12):** Open-Meteo API & geocoding, JSON parsing, Pandas forecast analysis, configurable alert engine, Plotly/Matplotlib charts, Streamlit dashboard, weather insights, CSV/JSON report export, SQLite storage, automated `pytest` suite, and GitHub deployment.

## 6. Documentation Index
See [README.md](./README.md) in `docs/` for the full documentation index.
