# API Documentation

**Author:** Akash Das  
**Status:** Phase 3 Configured (Provider & parameters configured; live HTTP fetching planned for Phase 4)  
**Last Updated:** 2026-11-27

## 1. Implementation Status
- **Configured & Verified (Phase 3):** Centralized Open-Meteo endpoints, query parameter builders, default units, timezone behavior, and custom exception hierarchy in `src/weather_app/core/config.py`, `src/weather_app/core/exceptions.py`, `src/weather_app/api/client.py`, and `src/weather_app/api/geocoding.py`.
- **Planned (Phase 4+):** Live HTTP requests (`requests`), response parsing, and error recovery.

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

## 5. Planned Error Handling (Phase 4–5)
- `APITimeoutError`: Request exceeds `DEFAULT_REQUEST_TIMEOUT_SECONDS` (10s)
- `APIConnectionError`: Network/DNS failure
- `APIError`: Non-200 HTTP status codes
- `LocationNotFoundError` / `GeocodingError`: Empty or invalid geocoding results
- Safe JSON validation for missing/malformed fields (Phase 5)
