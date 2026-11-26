# Development Roadmap

**Project:** Weather Forecast & Alert Application System  
**Author:** Akash Das

## Official 12-Phase Sequence

1. **Phase 1 — Environment Setup** *(Approved)*
2. **Phase 2 — Project Folder Creation** *(Approved)*
3. **Phase 3 — Weather API / API Key Setup** *(Approved)*
4. **Phase 4 — Weather Data Fetching** *(Approved)*
5. **Phase 5 — JSON Data Parsing** *(Approved)*
6. **Phase 6 — Forecast Analysis** *(Approved)*
   - Public interface: `analyze_forecast(forecast: WeatherForecast) -> ForecastAnalysis` in `src/weather_app/analysis/forecast_analysis.py`.
   - Result models: `ForecastAnalysis`, `CurrentConditionSummary`, `TemperatureAnalysis`, `HumidityAnalysis`, `PrecipitationAnalysis`, `WindAnalysis`, `DailyConditionSummary`, and `HourlyConditionSummary` (exposed via `hourly_summaries` for every hourly record).
   - Behavior: Excludes missing (`None`) values without substituting `0`, maps WMO weather codes via `describe_weather_code()`, and preserves naive local timestamps/dates without UTC conversion.
7. **Phase 7 — Alert Condition Logic** *(Approved)*
   - Public interface: `evaluate_alerts(analysis: ForecastAnalysis, thresholds: AlertThresholds | None = None) -> AlertEvaluation` in `src/weather_app/alerts/`.
   - Educational advisories only (not official meteorological warnings).
8. **Phase 8 — Weather Visualization** *(Completed — Awaiting Review)*
   - Reusable Plotly chart functions in `src/weather_app/visualization/charts.py` (Streamlit-independent).
9. **Phase 9 — Streamlit Dashboard** *(Next Phase)*
10. **Phase 10 — Insights and Interpretation**
11. **Phase 11 — Report Generation and Testing**
12. **Phase 12 — GitHub Upload and Deployment**
