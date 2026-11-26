"""Offline unit and integration tests for Phase 11 report generation, dashboard export, and CLI."""

from __future__ import annotations

import copy
import csv
from dataclasses import replace
from datetime import date, datetime
import io
import json
from pathlib import Path
import sys
from unittest.mock import patch

import pytest
from streamlit.testing.v1 import AppTest

from weather_app.alerts import AlertThresholds, evaluate_alerts
from weather_app.analysis import analyze_forecast, generate_weather_insights
from weather_app.core.exceptions import LocationNotFoundError, ReportExportError
from weather_app.models import (
    CurrentWeather,
    DailyForecast,
    ForecastMetadata,
    HourlyForecast,
    LocationInfo,
    WeatherForecast,
)
from weather_app.reporting import (
    DATA_ATTRIBUTION,
    ReportFormat,
    build_safe_filename,
    export_weather_report,
    generate_forecast_csv,
    generate_human_report,
    generate_report_json,
    resolve_safe_output_path,
    write_report_file,
)
from weather_app.services.forecast_service import DashboardWeatherBundle

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_PATH = str(PROJECT_ROOT / "app.py")
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import generate_report as cli_script  # noqa: E402


def _sample_location(name: str = "Kolkata") -> LocationInfo:
    return LocationInfo(
        name=name,
        latitude=22.56263,
        longitude=88.36304,
        timezone="Asia/Kolkata",
        country="India",
        country_code="IN",
        admin1="West Bengal",
        elevation=9.0,
        population=4631392,
        location_id=1275004,
    )


def _sample_bundle(
    *,
    high_temp: float = 36.0,
    include_missing: bool = True,
    empty_series: bool = False,
    omit_insights: bool = False,
) -> DashboardWeatherBundle:
    metadata = ForecastMetadata(
        latitude=22.56263,
        longitude=88.36304,
        timezone="Asia/Kolkata",
        timezone_abbreviation="IST",
        elevation=9.0,
        utc_offset_seconds=19800,
    )
    current = CurrentWeather(
        time=datetime(2026, 11, 27, 12, 0),
        temperature_2m=high_temp,
        relative_humidity_2m=None if include_missing else 65.0,
        apparent_temperature=high_temp + 2.0,
        precipitation=None if include_missing else 0.0,
        rain=None,
        wind_speed_10m=12.0,
        wind_direction_10m=180.0,
        weather_code=1,
    )
    hourly = () if empty_series else (
        HourlyForecast(
            time=datetime(2026, 11, 27, 12, 0),
            temperature_2m=high_temp,
            relative_humidity_2m=None if include_missing else 65.0,
            precipitation_probability=None if include_missing else 10.0,
            precipitation=None if include_missing else 0.0,
            wind_speed_10m=12.0,
            wind_direction_10m=180.0,
            weather_code=1,
        ),
        HourlyForecast(
            time=datetime(2026, 11, 27, 15, 0),
            temperature_2m=high_temp - 3.0,
            relative_humidity_2m=70.0,
            precipitation_probability=60.0,
            precipitation=4.5,
            wind_speed_10m=18.0,
            wind_direction_10m=190.0,
            weather_code=61,
        ),
    )
    daily = () if empty_series else (
        DailyForecast(
            date=date(2026, 11, 27),
            temperature_2m_max=high_temp,
            temperature_2m_min=22.0,
            precipitation_sum=None if include_missing else 4.5,
            precipitation_probability_max=60.0,
            wind_speed_10m_max=18.0,
            weather_code=61,
            sunrise=datetime(2026, 11, 27, 5, 58),
            sunset=datetime(2026, 11, 27, 16, 52),
        ),
    )
    forecast = WeatherForecast(
        metadata=metadata,
        current=current,
        hourly=hourly,
        daily=daily,
    )
    analysis = analyze_forecast(forecast)
    evaluation = evaluate_alerts(analysis, thresholds=AlertThresholds())
    insights = None if omit_insights else generate_weather_insights(analysis, evaluation=evaluation)
    return DashboardWeatherBundle(
        forecast=forecast,
        analysis=analysis,
        alert_evaluation=evaluation,
        insights=insights,  # type: ignore[arg-type]
    )


class TestCSVExport:
    """Tests for structured CSV forecast export."""

    def test_hourly_csv_headers_units_and_missing_values(self) -> None:
        bundle = _sample_bundle(include_missing=True)
        csv_text = generate_forecast_csv(bundle.forecast, series="hourly")
        rows = list(csv.reader(io.StringIO(csv_text)))

        assert rows[0] == [
            "Location Latitude",
            "Location Longitude",
            "Timezone",
            "Local Time",
            "Temperature (°C)",
            "Relative Humidity (%)",
            "Precipitation (mm)",
            "Precipitation Probability (%)",
            "Wind Speed (km/h)",
            "Wind Direction (°)",
            "WMO Weather Code",
            "Weather Condition",
            f"Data Attribution ({DATA_ATTRIBUTION})",
        ]
        assert len(rows) == 3
        # Missing values must remain empty strings, never converted to 0
        assert rows[1][3] == "2026-11-27T12:00:00"
        assert rows[1][5] == ""
        assert rows[1][6] == ""
        assert rows[1][7] == ""
        assert rows[1][11] == "Mainly clear"
        assert rows[1][12] == DATA_ATTRIBUTION
        assert rows[2][11] == "Slight rain"
        assert "Open-Meteo" in rows[1][12]
        assert "CC BY 4.0" in rows[1][12]
        assert "GeoNames" in rows[1][12]

    def test_daily_csv_and_empty_series(self) -> None:
        bundle = _sample_bundle(include_missing=True)
        daily_csv = generate_forecast_csv(bundle.forecast, series="daily")
        rows = list(csv.reader(io.StringIO(daily_csv)))
        assert len(rows) == 2
        assert rows[0][3] == "Local Date"
        assert rows[1][3] == "2026-11-27"
        assert rows[1][6] == ""  # missing precipitation_sum remains empty
        assert rows[1][13] == DATA_ATTRIBUTION

        empty_bundle = _sample_bundle(empty_series=True)
        empty_csv = generate_forecast_csv(empty_bundle.forecast, series="hourly")
        empty_rows = list(csv.reader(io.StringIO(empty_csv)))
        assert len(empty_rows) == 1  # headers only
        assert DATA_ATTRIBUTION in empty_rows[0][-1]
        assert "Open-Meteo" in empty_rows[0][-1]
        assert "CC BY 4.0" in empty_rows[0][-1]
        assert "GeoNames" in empty_rows[0][-1]

        empty_daily_csv = generate_forecast_csv(empty_bundle.forecast, series="daily")
        empty_daily_rows = list(csv.reader(io.StringIO(empty_daily_csv)))
        assert len(empty_daily_rows) == 1
        assert DATA_ATTRIBUTION in empty_daily_rows[0][-1]

    def test_invalid_series_raises_report_export_error(self) -> None:
        bundle = _sample_bundle()
        with pytest.raises(ReportExportError):
            generate_forecast_csv(bundle.forecast, series="weekly")


class TestJSONExport:
    """Tests for structured JSON export."""

    def test_json_validity_datetimes_nulls_and_no_secrets(self) -> None:
        bundle = _sample_bundle(include_missing=True)
        location = _sample_location()
        raw_json = generate_report_json(bundle, location=location)
        parsed = json.loads(raw_json)

        assert parsed["report_metadata"]["local_timezone"] == "Asia/Kolkata"
        assert parsed["report_metadata"]["observation_time_local"] == "2026-11-27T12:00:00"
        assert parsed["report_metadata"]["attribution"] == DATA_ATTRIBUTION
        assert "Open-Meteo" in parsed["report_metadata"]["attribution"]
        assert "CC BY 4.0" in parsed["report_metadata"]["attribution"]
        assert "GeoNames" in parsed["report_metadata"]["attribution"]
        assert "generated by this application" in parsed["report_metadata"]["attribution"]
        assert parsed["location"]["name"] == "Kolkata"
        assert parsed["forecast"]["current"]["relative_humidity_2m"] is None
        assert parsed["forecast"]["hourly"][0]["precipitation"] is None
        assert parsed["advisories"]["total_count"] > 0
        assert parsed["insights"]["overview"]
        assert "api_key" not in raw_json.lower()
        assert "secret" not in raw_json.lower()


class TestHumanReport:
    """Tests for human-readable Markdown report generation."""

    def test_human_report_sections_alerts_and_disclaimers(self) -> None:
        bundle = _sample_bundle(high_temp=36.0, include_missing=True)
        report = generate_human_report(bundle, location=_sample_location())

        for heading in (
            "## 1. Location & Forecast Metadata",
            "## 2. Current Conditions",
            "## 3. Forecast Overview",
            "## 4. Temperature Patterns",
            "## 5. Precipitation Outlook",
            "## 6. Humidity & Wind",
            "## 7. Weather-Condition Changes",
            "## 8. Educational Advisories",
            "## 9. Generated Insights Summary",
            "## 10. Disclaimers & Attribution",
        ):
            assert heading in report

        assert "Asia/Kolkata (IST)" in report
        assert "Relative Humidity:** Unavailable" in report
        assert "Triggered Advisories:" in report
        assert "not an official meteorological warning" in report.lower()
        assert DATA_ATTRIBUTION in report
        assert "not authored or endorsed by Open-Meteo or GeoNames" in report

    def test_human_report_no_alerts_and_unavailable_insights(self) -> None:
        bundle = _sample_bundle(
            high_temp=24.0,
            include_missing=False,
            empty_series=True,
            omit_insights=True,
        )
        # Ensure no alerts triggered by setting high precip threshold if needed
        assert bundle.alert_evaluation.total_count == 0
        report = generate_human_report(bundle, location=None)

        assert "No educational advisories were triggered for the available measurements" in report
        assert "missing or unavailable measurements were not evaluated" in report
        assert "Insights unavailable" in report
        assert "Generated insights are unavailable." in report
        assert "No daily forecast records are available." in report


class TestFileHandlingAndSafety:
    """Tests for safe filenames, path traversal protection, determinism, and immutability."""

    def test_safe_filename_and_path_traversal_rejection(self, tmp_path: Path) -> None:
        bundle = _sample_bundle()
        unsafe_loc = _sample_location(name="../../etc/passwd?Kolkata!")
        filename = build_safe_filename(unsafe_loc, bundle.forecast, ReportFormat.JSON)
        assert "/" not in filename
        assert "\\" not in filename
        assert ".." not in filename
        assert filename.endswith(".json")

        with pytest.raises(ReportExportError):
            resolve_safe_output_path(tmp_path, "../escape.json")
        with pytest.raises(ReportExportError):
            resolve_safe_output_path(tmp_path, "sub/file.json")

    def test_export_creates_missing_directories_and_handles_oserror(self, tmp_path: Path) -> None:
        bundle = _sample_bundle()
        nested_dir = tmp_path / "nested" / "exports"
        written = export_weather_report(
            bundle,
            "csv",
            location=_sample_location(),
            output_dir=nested_dir,
            series="hourly",
        )
        assert written.exists()
        assert written.parent == nested_dir.resolve()
        # UTF-8 with BOM for spreadsheet compatibility
        assert written.read_bytes().startswith(b"\xef\xbb\xbf")

        with patch.object(Path, "write_text", side_effect=OSError("disk full")):
            with pytest.raises(ReportExportError, match="Failed to write report file"):
                write_report_file("data", tmp_path / "fail.txt")

    def test_deterministic_output_and_no_input_mutation(self) -> None:
        bundle = _sample_bundle()
        location = _sample_location()
        bundle_before = copy.deepcopy(bundle)
        location_before = copy.deepcopy(location)

        assert generate_forecast_csv(bundle.forecast) == generate_forecast_csv(bundle.forecast)
        assert generate_report_json(bundle, location) == generate_report_json(bundle, location)
        assert generate_human_report(bundle, location) == generate_human_report(bundle, location)
        assert bundle == bundle_before
        assert location == location_before


class TestDashboardAndCLIIntegration:
    """Offline tests for Streamlit dashboard export controls and CLI workflow."""

    def test_dashboard_export_buttons_without_extra_api_calls(self) -> None:
        location = _sample_location()
        bundle = _sample_bundle()

        with (
            patch("weather_app.services.forecast_service.search_locations", return_value=[location]) as mock_search,
            patch("weather_app.services.forecast_service.get_weather_dashboard_data", return_value=bundle) as mock_fetch,
        ):
            at = AppTest.from_file(APP_PATH, default_timeout=15).run()
            at.sidebar.text_input[0].input("Kolkata")
            at.sidebar.button[0].click().run()
            assert mock_search.call_count == 1
            assert mock_fetch.call_count == 0

            # Click Fetch Forecast
            at.sidebar.button[1].click().run()
            assert not at.exception
            assert mock_fetch.call_count == 1
            assert any("Export Report" in s.value for s in at.subheader)

            # Ordinary rerun after fetch must not trigger another API call
            at.run()
            assert not at.exception
            assert mock_fetch.call_count == 1

    def test_cli_export_all_formats_offline(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        location = _sample_location()
        bundle = _sample_bundle()

        with (
            patch("generate_report.search_locations", return_value=[location]),
            patch("generate_report.get_weather_dashboard_data", return_value=bundle),
        ):
            exit_code = cli_script.main(
                ["--city", "Kolkata", "--format", "all", "--output-dir", str(tmp_path)]
            )

        assert exit_code == 0
        out = capsys.readouterr().out
        assert "Resolved location: Kolkata" in out
        exported_files = list(tmp_path.iterdir())
        assert {p.suffix for p in exported_files} == {".csv", ".json", ".md"}

    def test_cli_handles_location_not_found(self, capsys: pytest.CaptureFixture[str]) -> None:
        with patch("generate_report.search_locations", side_effect=LocationNotFoundError("No results")):
            exit_code = cli_script.main(["--city", "NowhereCity"])

        assert exit_code == 1
        assert "Report generation failed" in capsys.readouterr().err
