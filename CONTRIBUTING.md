# Contributing Guidelines

Thank you for your interest in contributing to the **Weather Forecast & Alert Application** by **Akash Das**.

## Development Setup
1. Clone the repository and open the project root.
2. Activate the local virtual environment (`.venv`):
   - **Windows PowerShell:** `.venv\Scripts\Activate.ps1`
   - **Linux/macOS:** `source .venv/bin/activate`
3. Install dependencies from `requirements.txt` once added in subsequent phases.

## Coding Conventions
- Follow PEP 8 and keep modules focused on single responsibilities under `src/weather_app/`.
- Include type hints and concise docstrings for public functions and classes.
- Never commit `.env` files, API keys, or generated outputs.

## Branching & Pull Request Expectations
- Create a descriptive feature or fix branch from `main` (e.g., `feature/open-meteo-client`, `fix/alert-threshold`).
- Keep pull requests focused on a single phase or task and update relevant files in `docs/` when architecture or usage changes.

## Testing Expectations
- Add or update unit tests in `tests/` for new or modified functionality.
- Ensure `python -m pytest` passes before opening a pull request (see [docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md)).
