# Dataset & Features

**Author:** Akash Das  
**Status:** Phase 5 Implemented (Structured models & JSON parsing; Phase 6 analysis planned next)  
**Last Updated:** 2026-11-27

## 1. Raw API JSON vs. Structured Application Models
- **Raw API JSON:** Nested Open-Meteo dictionaries containing parallel arrays (`hourly.time`, `hourly.temperature_2m`, etc.) and ISO-8601 strings, returned by Phase 4 clients (`WeatherAPIClient`, `GeocodingClient`).
- **Structured Models (`src/weather_app/models/weather.py`):** Immutable Python 3.11 dataclasses (`LocationInfo`, `ForecastMetadata`, `CurrentWeather`, `HourlyForecast`, `DailyForecast`, `WeatherForecast`) with typed numeric fields and parsed `datetime` / `date` objects.

## 2. Sample Data (`data/sample/sample_weather.json`)
- Updated to reflect a representative Open-Meteo response structure containing `latitude`, `longitude`, `timezone`, `current`, `hourly`, and `daily` sections aligned with Phase 3 configured variables.

## 3. Model Fields & Data Types
- **`LocationInfo`:** `name: str`, `latitude: float`, `longitude: float`, optional `timezone`, `country`, `country_code`, `admin1`, `elevation`, `population`, `location_id`.
- **`ForecastMetadata`:** `latitude: float`, `longitude: float`, `timezone: str`, optional `timezone_abbreviation`, `elevation`, `utc_offset_seconds`.
- **`CurrentWeather`:** `time: datetime`, `temperature_2m: float`, optional `relative_humidity_2m`, `apparent_temperature`, `precipitation`, `rain`, `wind_speed_10m`, `wind_direction_10m`, `weather_code`.
- **`HourlyForecast`:** `time: datetime`, `temperature_2m: float`, optional `relative_humidity_2m`, `precipitation_probability`, `precipitation`, `wind_speed_10m`, `wind_direction_10m`, `weather_code`.
- **`DailyForecast`:** `date: date`, `temperature_2m_max: float`, `temperature_2m_min: float`, optional `precipitation_sum`, `precipitation_probability_max`, `wind_speed_10m_max`, `weather_code`, `sunrise: datetime | None`, `sunset: datetime | None`.
- **`WeatherForecast`:** `metadata`, `current`, `hourly: tuple[HourlyForecast, ...]`, `daily: tuple[DailyForecast, ...]`.

## 4. Parsing Behavior & Boundary
- **Implemented (Phase 5):** `parse_forecast_response()` and `parse_geocoding_response()` in `src/weather_app/services/weather_service.py` validate required fields, coordinate bounds, array length consistency, and ISO-8601 dates/times, raising `DataParsingError` on invalid input.
- **Planned (Phase 6+):** Statistical trend analysis, Pandas transformations, alert thresholds, and visualizations (the parser itself performs no weather analysis).

## 5. Running Parsing Tests
```powershell
.venv\Scripts\python.exe -m pytest tests/test_parsing.py -v
```
