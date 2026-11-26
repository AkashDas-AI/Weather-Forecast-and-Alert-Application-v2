# Testing Guide

**Author:** Akash Das  
**Status:** Phase 9 Active (`pytest`, `plotly`, and `streamlit` installed in `.venv`; offline tests for API, parsing, analysis, alerts, visualizations, and dashboard)  
**Last Updated:** 2026-11-27

## 1. Testing Approach
Automated tests live in `tests/` and use `pytest` (configured in `pyproject.toml` with `pythonpath = ["src"]`).

## 2. Activating `.venv`
Before running tests, activate the project virtual environment:
```powershell
.venv\Scripts\Activate.ps1
```

## 3. Running Tests
- **Run the full test suite:**
  ```powershell
  .venv\Scripts\python.exe -m pytest -v
  ```
- **Run an individual test file:**
  ```powershell
  .venv\Scripts\python.exe -m pytest tests/test_alerts.py -v
  ```
- **Run a specific test function:**
  ```powershell
  .venv\Scripts\python.exe -m pytest tests/test_alerts.py -k "test_name"
  ```

## 4. Interpreting Test Results
- `PASSED`: The test assertion succeeded.
- `FAILED`: An assertion failed or an unexpected exception occurred; inspect the traceback for the failing module.
- `SKIPPED`: The test was intentionally skipped.

## 5. Reporting Bugs
When reporting an issue, include the command executed, the Python/OS environment, the full traceback, and steps to reproduce.
