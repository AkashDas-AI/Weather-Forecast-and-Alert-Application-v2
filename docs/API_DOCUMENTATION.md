# API Documentation

**Author:** Akash Das  
**Status:** Phase 4 Implemented (Live HTTP fetching for Forecast & Geocoding; domain model parsing planned for Phase 5)  
**Last Updated:** 2026-11-27

## 1. Implementation Status
- **Implemented & Verified (Phase 3–4):**
  - Centralized Open-Meteo endpoints, query parameter builders, default units, timezone behavior, and custom exception hierarchy in `src/weather_app/core/config.py` and `src/weather_app/core/exceptions.py`.
  - Shared HTTP GET JSON helper (`src/weather_app/api/_http.py`) using `requests.get()` with configured request timeouts.
  - `WeatherAPIClient.fetch_forecast()` (`src/weather_app/api/client.py`) for retrieving raw forecast JSON dictionaries with coordinate/horizon validation.
  - `GeocodingClient.search_location()` (`src/weather_app/api/geocoding.py`) for retrieving raw geocoding JSON dictionaries with query validation and `LocationNotFoundError` handling.
  - Mocked unit test suite in `tests/test_api.py` (runs offline via `.venv\Scripts\python.exe -m pytest`).
- **Planned (Phase 5+):** JSON-to-domain-model parsing, Pandas forecast analysis, alert rules, and dashboard UI.

## 2. Selected Weather Provider
- **Provider:** **Open-Meteo** ([open-meteo.com](https://open-meteo.com/))
- **Selection Rationale:**
  - Public forecast and geocoding access without requiring an API key for standard non-commercial use.
  - Supports current, hourly, and daily weather variables in a single forecast endpoint.
  - Provides a dedicated geocoding API for city-to-coordinate resolution.
  - Well suited for educational and portfolio Python applications.
- **API Key Requirement:** **None** for standard non-commercial use. No API key is invented or required.
- **Usage Terms & Limits (`https://open-meteo.com/en/terms`):**
  - Free access is restricted to **educational, non-commercial, and open-source use** subject to the provider's terms (not for unrestricted commercial use).
  - Free non-commercial API limits:
    - Fewer than **10,000** API calls per day
    - **5,000** API calls per hour
    - **600** API calls per minute
    - **300,000** API calls per month
  - Forecast horizon defaults to 7 days (provider supports up to 16 days); daily variables require a `timezone` parameter.
- **Data Attribution:**
  - **Weather Data:** Provided by **Open-Meteo** under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** licence ([open-meteo.com/en/license](https://open-meteo.com/en/license)). Appropriate credit must be given, a link to the licence must be provided, and any modifications to the data must be indicated where applicable.
  - **Geocoding Data:** Location search data is provided by **GeoNames** via the Open-Meteo Geocoding API ([open-meteo.com/en/docs/geocoding-api](https://open-meteo.com/en/docs/geocoding-api)). GeoNames is the underlying location database and is distinct from Open-Meteo's weather forecast data.

## 3. Forecast API (`https://api.open-meteo.com/v1/forecast`)
- **Official Docs:** https://open-meteo.com/en/docs
- **General Request Parameters:**
  - `latitude`, `longitude`: WGS84 geographic coordinates
  - `timezone`: `auto` (resolves local timezone from coordinates; required for `daily` aggregations)
  - `forecast_days`: `7` (7-day default horizon)
  - `temperature_unit`: `celsius` (supports `celsius`, `fahrenheit`)
  - `wind_speed_unit`: `kmh` (supports `kmh`, `ms`, `mph`, `kn`)
  - `precipitation_unit`: `mm` (supports `mm`, `inch`)
- **Configured Weather Variables:**
  - `current`: `temperature_2m`, `relative_humidity_2m`, `apparent_temperature`, `precipitation`, `rain`, `wind_speed_10m`, `wind_direction_10m`, `weather_code`
  - `hourly`: `temperature_2m`, `relative_humidity_2m`, `precipitation_probability`, `precipitation`, `wind_speed_10m`, `wind_direction_10m`, `weather_code`
  - `daily`: `temperature_2m_max`, `temperature_2m_min`, `precipitation_sum`, `precipitation_probability_max`, `wind_speed_10m_max`, `weather_code`, `sunrise`, `sunset`

## 4. Geocoding API (`https://geocoding-api.open-meteo.com/v1/search`)
- **Official Docs:** https://open-meteo.com/en/docs/geocoding-api
- **Why Geocoding is Needed:** The Forecast API requires numeric `latitude` and `longitude`, whereas users search by city or place name.
- **Configured Search Parameters:**
  - `name`: User-entered location query (required)
  - `count`: `5` (returns multiple candidates so ambiguous city names can be disambiguated by country/admin region)
  - `language`: `en`
  - `format`: `json`
- **Expected Response Fields (`results`):** `id`, `name`, `latitude`, `longitude`, `country`, `country_code`, `admin1`, `timezone`, `elevation`, `population`.

## 5. Timeout & Error Handling (Implemented in Phase 4)
- **Request Timeout:** All HTTP GET calls pass `APIConfig.timeout_seconds` (default `10` seconds) to `requests.get()`.
- **Exception Translation (`src/weather_app/api/_http.py`):**
  - `requests.exceptions.Timeout` → `APITimeoutError`
  - `requests.exceptions.ConnectionError` → `APIConnectionError`
  - `requests.exceptions.HTTPError` → `APIError` (preserves `status_code`)
  - `requests.exceptions.RequestException` → `APIError`
  - Malformed or non-object JSON responses → `APIError`
  - Empty or missing `results` in geocoding responses → `LocationNotFoundError`
  - Invalid coordinates, `forecast_days`, `query`, or `count` → `ValueError`
- **Phase 5 Boundary:** Safe extraction and validation of nested weather fields into domain models will be implemented in Phase 5.
