# Testing Guide

**Author:** Akash Das  
**Status:** Phase 2 (Test scaffolds created; full test suite planned for Phases 3–11)  
**Last Updated:** 2026-11-27

## 1. Testing Approach
Automated tests live in `tests/` and use `pytest` (configured in `pyproject.toml` with `pythonpath = ["src"]`).

## 2. Activating `.venv`
Before running tests, activate the project virtual environment:
```powershell
.venv\Scripts\Activate.ps1
```

## 3. Running Tests (Once `pytest` is Installed in Later Phases)
- **Run the full test suite:**
  ```powershell
  python -m pytest
  ```
- **Run an individual test file:**
  ```powershell
  python -m pytest tests/test_api.py
  ```
- **Run a specific test function:**
  ```powershell
  python -m pytest tests/test_alerts.py -k "test_name"
  ```

## 4. Interpreting Test Results
- `PASSED`: The test assertion succeeded.
- `FAILED`: An assertion failed or an unexpected exception occurred; inspect the traceback for the failing module.
- `SKIPPED`: The test was intentionally skipped.

## 5. Reporting Bugs
When reporting an issue, include the command executed, the Python/OS environment, the full traceback, and steps to reproduce.
