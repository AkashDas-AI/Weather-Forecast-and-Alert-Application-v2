"""Configurable weather alert rules and evaluation package."""

from weather_app.alerts.alert_engine import (
    EDUCATIONAL_DISCLAIMER,
    AlertCategory,
    AlertEvaluation,
    AlertScope,
    AlertSeverity,
    WeatherAlert,
    evaluate_alerts,
)
from weather_app.alerts.thresholds import (
    DEFAULT_SEVERE_WEATHER_CODES,
    AlertThresholds,
)

__all__ = [
    "AlertCategory",
    "AlertEvaluation",
    "AlertScope",
    "AlertSeverity",
    "AlertThresholds",
    "DEFAULT_SEVERE_WEATHER_CODES",
    "EDUCATIONAL_DISCLAIMER",
    "WeatherAlert",
    "evaluate_alerts",
]
