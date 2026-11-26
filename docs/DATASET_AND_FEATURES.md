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

## 4. Parsing & Analysis Behavior
- **Implemented (Phase 5):** `parse_forecast_response()` and `parse_geocoding_response()` in `src/weather_app/services/weather_service.py` validate required fields, coordinate bounds, array length consistency, and ISO-8601 dates/times, raising `DataParsingError` on invalid input.
- **Implemented (Phase 6):** `analyze_forecast()` in `src/weather_app/analysis/forecast_analysis.py` computes structured summaries (`ForecastAnalysis`) from `WeatherForecast`:
  - **Temperature:** Current, apparent, hourly mean/min/max, daily min/max, and sample-count sufficiency flags.
  - **Humidity:** Current and hourly mean/min/max over non-null observations.
  - **Precipitation:** Separates amounts in `mm` (`current_mm`, `hourly_total_mm`, `hourly_max_mm`, `daily_total_mm`) from probabilities in `%` (`hourly_max_probability_pct`, `hourly_avg_probability_pct`, `daily_max_probability_pct`).
  - **Wind:** Current speed/direction and hourly average/max + daily max speeds (`km/h`) without inferring storm severity.
  - **Weather Codes:** Maps WMO/Open-Meteo codes (`WMO_WEATHER_CODES`) via `describe_weather_code()`, falling back to `"Unknown weather condition"`.
  - **Missing Data & Timezones:** Missing/`None` observations are excluded from averages/sums (never replaced with `0`). Naive local timestamps from Open-Meteo are preserved as-is without UTC conversion so `local_date` and `hourly_dates` match the forecast's local timezone.
  - **Limitations & Phase 7 Boundary:** Analysis provides educational descriptive statistics only (not official meteorological warnings or scientifically validated risk predictions). Threshold-based alert evaluation is deferred to Phase 7.

## 5. Running Parsing & Analysis Tests
```powershell
.venv\Scripts\python.exe -m pytest tests/test_parsing.py tests/test_analysis.py -v
```
