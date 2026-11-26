# API Documentation

**Author:** Akash Das  
**Status:** Planned (API integration will be implemented in Phases 3–4)  
**Last Updated:** 2026-11-27

## 1. Implementation Status
- **Implemented:** Module scaffolds only (`src/weather_app/api/client.py`, `src/weather_app/api/geocoding.py`) and `.env.example` placeholder (`WEATHER_PROVIDER=open-meteo`).
- **Planned:** Live HTTP requests, geocoding, timeout handling, and response parsing.

## 2. Planned Weather Provider
- **Primary Provider:** Open-Meteo (public forecast and geocoding APIs; no API key required for standard usage).
- **Modularity:** `api/client.py` will abstract provider calls so alternative providers can be added later via configuration.

## 3. Planned Endpoints & Structure
- **Geocoding Endpoint (Planned):** Resolves city/location names into `latitude`, `longitude`, `timezone`, and display name.
- **Forecast Endpoint (Planned):** Accepts `latitude`, `longitude`, and requested `current`, `hourly`, and `daily` weather variables, returning JSON.

## 4. Planned Error Handling
- Request timeouts and connection failures
- Non-200 HTTP status codes
- Empty geocoding results (unknown location)
- Malformed or incomplete JSON payloads (handled safely in Phase 5)
