"""Shared HTTP GET JSON helper for weather and geocoding API clients.

Author: Akash Das
"""

from typing import Any

import requests

from weather_app.core.exceptions import APIConnectionError, APIError, APITimeoutError


def perform_get_json(url: str, params: dict[str, Any], timeout: int) -> dict[str, Any]:
    """Execute an HTTP GET request and return the decoded JSON object.

    Translates network, timeout, HTTP status, and JSON decoding failures into
    application-specific APIError subclasses without exposing sensitive context.
    """
    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.Timeout as exc:
        raise APITimeoutError(
            f"Request to {url} timed out after {timeout} seconds."
        ) from exc
    except requests.exceptions.ConnectionError as exc:
        raise APIConnectionError(
            f"Failed to connect to {url}."
        ) from exc
    except requests.exceptions.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else None
        raise APIError(
            f"HTTP error {status_code} returned from {url}.",
            status_code=status_code,
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise APIError(f"Unexpected request error for {url}: {exc}") from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise APIError(
            f"Malformed JSON response received from {url}.",
            status_code=response.status_code,
        ) from exc

    if not isinstance(payload, dict):
        raise APIError(
            f"Unexpected JSON payload type from {url}: expected object.",
            status_code=response.status_code,
        )

    return payload
