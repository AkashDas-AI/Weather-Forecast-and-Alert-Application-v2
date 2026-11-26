# Reports Directory

This directory stores documentation related to generated weather reports. Runtime report exports are written to `outputs/exports/` (ignored by Git except for `.gitkeep`).

## Supported Export Formats
- **CSV (`.csv`)**: Hourly or daily forecast series (`generate_forecast_csv`), encoded as UTF-8 with BOM (`utf-8-sig`) for spreadsheet compatibility, preserving missing measurements as empty cells.
- **JSON (`.json`)**: Structured report payload (`generate_report_json`) containing metadata, location, forecast, analysis, educational advisories, and insights with ISO-8601 local timestamps and `null` for missing values.
- **Markdown (`.md`)**: Human-readable report (`generate_human_report`) summarizing conditions, trends, educational advisories, generated insights, and attribution/disclaimers.

## Usage
- **Dashboard:** Click **Download Hourly CSV**, **Download Daily CSV**, **Download JSON**, or **Download Report (MD)** in the **Export Report** section of `app.py` (uses cached state; no extra API calls).
- **CLI:**
  ```powershell
  .venv\Scripts\python.exe scripts/generate_report.py --city "Kolkata" --format all
  ```
