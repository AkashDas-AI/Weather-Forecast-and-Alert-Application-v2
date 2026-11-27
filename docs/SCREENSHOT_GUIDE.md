# Screenshot Guide

**Author:** Akash Das  
**Status:** Active (Light & Dark Mode Dashboard Screenshots Captured)  
**Last Updated:** 2026-11-27

## 1. Capture Specifications
- **Application Entry Point:** `.venv\Scripts\python.exe -m streamlit run app.py`
- **Browser & Viewport:** Google Chrome desktop viewport at `1600 x 900` pixels (16:9 aspect ratio, `deviceScaleFactor: 1`, DevTools closed).
- **Data Source:** Live **Open-Meteo Forecast API** and **Open-Meteo Geocoding API** data fetched for **Kolkata, West Bengal, India** (`22.56, 88.36`, timezone `Asia/Kolkata`, local observation `2026-11-27 06:00`, `18.4 °C`, `Clear sky`).
- **Format:** Uncropped PNG files saved under `images/screenshots/`.

## 2. Screenshot Inventory

### Dark Mode (Default)
| Filename | Dimensions | Data Type | Dashboard Sections Covered |
| :--- | :--- | :--- | :--- |
| `images/screenshots/dashboard_overview_dark.png` | `1600 x 900` | Live Open-Meteo API | Sidebar Appearance toggle (Dark Mode ON), location search/selection, header, Current Weather metrics, Daily Forecast table |
| `images/screenshots/dashboard_forecast_details_dark.png` | `1600 x 900` | Live Open-Meteo API | Daily Forecast table and upper Weather Visualizations (`plotly_dark`) |
| `images/screenshots/dashboard_forecast_charts_dark.png` | `1600 x 900` | Live Open-Meteo API | Weather Visualizations Plotly charts (`plotly_dark`) |
| `images/screenshots/dashboard_advisories_insights_exports_dark.png` | `1600 x 900` | Live Open-Meteo API | Weather Advisories, Weather Insights & Interpretation, and Export Report buttons (Dark Mode) |

### Light Mode
| Filename | Dimensions | Data Type | Dashboard Sections Covered |
| :--- | :--- | :--- | :--- |
| `images/screenshots/dashboard_overview.png` | `1600 x 900` | Live Open-Meteo API | Sidebar Appearance toggle (Dark Mode OFF), location search/selection, header, Current Weather metrics, Daily Forecast table |
| `images/screenshots/dashboard_forecast_details.png` | `1600 x 900` | Live Open-Meteo API | Daily Forecast table and upper Weather Visualizations (`plotly_white`) |
| `images/screenshots/dashboard_forecast_charts.png` | `1600 x 900` | Live Open-Meteo API | Weather Visualizations Plotly charts (`plotly_white`) |
| `images/screenshots/dashboard_advisories_insights_exports.png` | `1600 x 900` | Live Open-Meteo API | Weather Advisories, Weather Insights & Interpretation, and Export Report buttons (Light Mode) |

## 3. Refreshing Screenshots After UI Changes
1. Launch the dashboard locally:
   ```powershell
   .venv\Scripts\python.exe -m streamlit run app.py
   ```
2. Open `http://localhost:8501` in a `1600 x 900` desktop browser window without DevTools or personal bookmarks visible.
3. Search for `Kolkata`, select `Kolkata, West Bengal, India`, and click **Fetch Forecast**.
4. Capture the four Dark Mode PNGs (`*_dark.png`).
5. Toggle **Dark Mode** off in the sidebar **Appearance** section and capture the four Light Mode PNGs.
6. Verify all eight PNGs are `1600 x 900`, legible, and free of secrets or personal data.
