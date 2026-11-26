"""Configurable educational alert threshold definitions.

Author: Akash Das

Note: All default values in this module are illustrative educational thresholds
and must not be treated as official or scientifically validated meteorological
warning criteria.
"""

from dataclasses import dataclass
from typing import Any

from weather_app.core.exceptions import ConfigurationError

DEFAULT_SEVERE_WEATHER_CODES: tuple[int, ...] = (65, 67, 75, 82, 86, 95, 96, 99)


def _validate_number(value: Any, field_name: str) -> float:
    """Validate that a threshold value is a real number (excluding bool)."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConfigurationError(f"Threshold '{field_name}' must be a valid number.")
    return float(value)


@dataclass(frozen=True)
class AlertThresholds:
    """Configurable thresholds for educational weather advisory evaluation.

    Units:
        - high_temp_c / low_temp_c: degrees Celsius (°C)
        - heavy_rain_hourly_mm: millimetres (mm)
        - heavy_rain_daily_mm: millimetres (mm)
        - high_precip_probability_pct: percentage (0–100 %)
        - high_humidity_pct: percentage (0–100 %)
        - strong_wind_kmh: kilometres per hour (km/h)
        - severe_weather_codes: WMO/Open-Meteo integer weather codes
    """

    high_temp_c: float = 35.0
    low_temp_c: float = 5.0
    heavy_rain_hourly_mm: float = 10.0
    heavy_rain_daily_mm: float = 50.0
    high_precip_probability_pct: float = 70.0
    high_humidity_pct: float = 85.0
    strong_wind_kmh: float = 50.0
    severe_weather_codes: tuple[int, ...] = DEFAULT_SEVERE_WEATHER_CODES

    def __post_init__(self) -> None:
        high_temp = _validate_number(self.high_temp_c, "high_temp_c")
        low_temp = _validate_number(self.low_temp_c, "low_temp_c")
        rain_hourly = _validate_number(self.heavy_rain_hourly_mm, "heavy_rain_hourly_mm")
        rain_daily = _validate_number(self.heavy_rain_daily_mm, "heavy_rain_daily_mm")
        precip_prob = _validate_number(
            self.high_precip_probability_pct, "high_precip_probability_pct"
        )
        humidity = _validate_number(self.high_humidity_pct, "high_humidity_pct")
        wind = _validate_number(self.strong_wind_kmh, "strong_wind_kmh")

        if low_temp >= high_temp:
            raise ConfigurationError(
                "Threshold 'low_temp_c' must be strictly less than 'high_temp_c'."
            )
        if rain_hourly <= 0.0:
            raise ConfigurationError("Threshold 'heavy_rain_hourly_mm' must be positive.")
        if rain_daily <= 0.0:
            raise ConfigurationError("Threshold 'heavy_rain_daily_mm' must be positive.")
        if not (0.0 <= precip_prob <= 100.0):
            raise ConfigurationError(
                "Threshold 'high_precip_probability_pct' must be between 0 and 100."
            )
        if not (0.0 <= humidity <= 100.0):
            raise ConfigurationError(
                "Threshold 'high_humidity_pct' must be between 0 and 100."
            )
        if wind <= 0.0:
            raise ConfigurationError("Threshold 'strong_wind_kmh' must be positive.")

        if not isinstance(self.severe_weather_codes, (tuple, list)) or len(
            self.severe_weather_codes
        ) == 0:
            raise ConfigurationError(
                "Threshold 'severe_weather_codes' must be a non-empty sequence of integers."
            )
        for code in self.severe_weather_codes:
            if isinstance(code, bool) or not isinstance(code, int):
                raise ConfigurationError(
                    "All entries in 'severe_weather_codes' must be integers."
                )
