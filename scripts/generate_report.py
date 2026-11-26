"""Standalone CLI script for generating weather forecast, analysis, and alert reports.

Author: Akash Das
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Sequence

_SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from weather_app.core.exceptions import WeatherAppError
from weather_app.models import LocationInfo
from weather_app.reporting import DEFAULT_EXPORT_DIR, export_weather_report
from weather_app.services.forecast_service import (
    format_location_label,
    get_weather_dashboard_data,
    search_locations,
)


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser for report generation."""
    parser = argparse.ArgumentParser(
        description="Generate weather forecast, analysis, advisory, and insight reports."
    )
    location_group = parser.add_mutually_exclusive_group(required=True)
    location_group.add_argument(
        "--city",
        type=str,
        help="City or location name to geocode via Open-Meteo.",
    )
    location_group.add_argument(
        "--lat",
        type=float,
        help="Latitude in decimal degrees (must be paired with --lon).",
    )
    parser.add_argument(
        "--lon",
        type=float,
        help="Longitude in decimal degrees (required when --lat is provided).",
    )
    parser.add_argument(
        "--format",
        dest="report_format",
        choices=("csv", "json", "md", "all"),
        default="all",
        help="Export format (default: all).",
    )
    parser.add_argument(
        "--series",
        choices=("hourly", "daily"),
        default="hourly",
        help="Forecast series to include in CSV exports (default: hourly).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_EXPORT_DIR,
        help="Directory where generated report files will be written.",
    )
    parser.add_argument(
        "--filename",
        type=str,
        default=None,
        help="Optional output filename (valid only when exporting a single format).",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the report-generation CLI workflow and return an exit status code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.lat is not None and args.lon is None:
        parser.error("--lon is required when --lat is provided.")
    if args.lat is None and args.lon is not None:
        parser.error("--lat is required when --lon is provided.")
    if args.filename is not None and args.report_format == "all":
        parser.error("--filename can only be used with a single --format (csv, json, or md).")

    try:
        selected_location: LocationInfo | None = None
        if args.city is not None:
            cleaned_city = args.city.strip()
            if not cleaned_city:
                print("Error: --city must not be empty.", file=sys.stderr)
                return 2
            matches = search_locations(cleaned_city)
            selected_location = matches[0]
            latitude = selected_location.latitude
            longitude = selected_location.longitude
            print(f"Resolved location: {format_location_label(selected_location)}")
        else:
            latitude = float(args.lat)
            longitude = float(args.lon)

        bundle = get_weather_dashboard_data(latitude=latitude, longitude=longitude)

        formats = ["csv", "json", "md"] if args.report_format == "all" else [args.report_format]
        written_paths: list[Path] = []
        for fmt in formats:
            path = export_weather_report(
                bundle,
                fmt,
                location=selected_location,
                output_dir=args.output_dir,
                filename=args.filename if len(formats) == 1 else None,
                series=args.series,
            )
            written_paths.append(path)

        for path in written_paths:
            print(f"Exported: {path}")
        return 0
    except WeatherAppError as exc:
        print(f"Report generation failed: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Unexpected error during report generation: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
