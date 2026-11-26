# Screenshot Guide

**Author:** Akash Das  
**Status:** Active (Live Dashboard Screenshots Captured in Phase 12 Stage 2)  
**Last Updated:** 2026-11-27

## 1. Capture Specifications
- **Application Entry Point:** `.venv\Scripts\python.exe -m streamlit run app.py`
- **Browser & Viewport:** Google Chrome desktop viewport at `1600 x 900` pixels (16:9 aspect ratio, `deviceScaleFactor: 1`, DevTools closed).
- **Data Source:** Live **Open-Meteo Forecast API** and **Open-Meteo Geocoding API** data fetched for **Kolkata, West Bengal, India** (`22.56, 88.36`, timezone `Asia/Kolkata`, local observation `2026-11-27 04:30`).
- **Format:** Uncropped PNG files saved under `images/screenshots/`.

## 2. Screenshot Inventory

| Filename | Dimensions | Data Type | Dashboard Sections Covered |
| :--- | :--- | :--- | :--- |
| `images/screenshots/dashboard_overview.png` | `1600 x 900` | Live Open-Meteo API | Sidebar location search/selection, application header, selected location banner, and **Current Weather** metrics |
| `images/screenshots/dashboard_forecast_details.png` | `1600 x 900` | Live Open-Meteo API | **Forecast Overview** (Daily and Hourly Forecast tabs/tables) and upper **Weather Visualizations** |
| `images/screenshots/dashboard_forecast_charts.png` | `1600 x 900` | Live Open-Meteo API | **Weather Visualizations** section displaying the interactive Plotly charts |
| `images/screenshots/dashboard_advisories_insights_exports.png` | `1600 x 900` | Live Open-Meteo API | **Weather Advisories**, **Weather Insights & Interpretation**, and **Export Report** download controls |

## 3. Refreshing Screenshots After UI Changes
1. Launch the dashboard locally:
   ```powershell
   .venv\Scripts\python.exe -m streamlit run app.py
   ```
2. Open `http://localhost:8501` in a `1600 x 900` desktop browser window without DevTools or personal bookmarks visible.
3. Search for a location (for example, `Kolkata`), select a result, and click **Fetch Forecast**.
4. Wait for all six Plotly charts, advisories, insights, and export buttons to finish rendering.
5. Capture clean PNGs and overwrite the corresponding files in `images/screenshots/`.
6. Ensure no API keys, secrets, or personal information appear in any screenshot.
