# Dataset & Features

**Author:** Akash Das  
**Status:** Phase 2 (Sample placeholder created; API schema & analysis planned for Phases 3–6)  
**Last Updated:** 2026-11-27

## 1. Sample Data (Implemented)
- **Location:** `data/sample/sample_weather.json`
- **Purpose:** Provides a minimal, valid JSON sample weather payload for Phase 2 structural validation and offline testing.
- **Current Sample Fields:** `metadata`, `latitude`, `longitude`, `timezone`, and `current` (`time`, `temperature_2m`, `relative_humidity_2m`, `wind_speed_10m`).

## 2. Planned Weather Variables (Phases 3–6)
When Open-Meteo integration is implemented, the application plans to retrieve and process:
- **Current Weather:** Temperature, relative humidity, wind speed, weather code, observation timestamp.
- **Hourly Forecast:** Hourly temperature, precipitation probability, humidity, wind speed.
- **Daily Forecast:** Daily min/max temperature, precipitation sum/probability, max wind speed.

## 3. Planned Application Features
- **Forecast Analysis:** Temperature trends, min/max/average summaries, rainfall risk windows, and wind/humidity summaries.
- **Configurable Alerts:** Rule-based advisories for high temperature, low temperature, heavy rainfall probability, high humidity, and strong wind.
- **Visualizations & Insights:** Trend charts and plain-language forecast summaries.
- **Export:** Structured CSV and JSON report generation into `outputs/exports/`.
