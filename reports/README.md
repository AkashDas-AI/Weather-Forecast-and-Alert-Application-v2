# Reports Directory

This directory stores documentation related to generated weather reports. Runtime report exports are written to `outputs/exports/` (ignored by Git except for `.gitkeep`).

## Supported Export Formats
- **CSV (`.csv`)**: Hourly or daily forecast series (`generate_forecast_csv`), encoded as UTF-8 with BOM (`utf-8-sig`) for spreadsheet compatibility, preserving missing measurements as empty cells and including Open-Meteo (CC BY 4.0), GeoNames, reformatting/processing notice, and derived-content attribution in the `Data Attribution` column/header (even when a series is empty).
- **JSON (`.json`)**: Structured report payload (`generate_report_json`) containing metadata (including `attribution`), location, forecast, analysis, educational advisories, and insights with ISO-8601 local timestamps and `null` for missing values.
- **Markdown (`.md`)**: Human-readable report (`generate_human_report`) summarizing conditions, trends, educational advisories, generated insights, and explicit attribution/disclaimers distinguishing source data from application-generated content.

## Usage
- **Dashboard:** Click **Download Hourly CSV**, **Download Daily CSV**, **Download JSON**, or **Download Report (MD)** in the **Export Report** section of `app.py` (uses cached state; no extra API calls).
- **CLI:**
  ```powershell
  .venv\Scripts\python.exe scripts/generate_report.py --city "Kolkata" --format all
  ```
