# ltasg SDK — Repository Guidelines

Async Python SDK wrapper for the LTA DataMall API (v6.8). Published as
`ltasg` on PyPI.

---

## Quick Start

```bash
git clone https://github.com/ashe0047/ltasg.git
cd ltasg
python -m pip install -e '.[dev]'
python -m pytest test/ -v --timeout=30
```

## Running Tests

```bash
# All non-network tests
python -m unittest test.test_unit test.test_integration -v

# Quick E2E tests (require LTA_API_KEY in .env)
python -m unittest test.test.TestQuickE2E -v

# Slow E2E tests (paginated endpoints, SLOW_TESTS=1)
SLOW_TESTS=1 python -m unittest test.test.TestSlowE2E -v

# Packaging integrity (requires build and packaging deps)
python -m pytest test/test_sdk_packaging.py -v
```

## Code Quality

```bash
pip install ruff mypy
ruff check src/ltasg/ test/
mypy src/ltasg/
```

## Conventional Commits

This project uses [Conventional Commits](https://www.conventionalcommits.org/)
for all commit messages. The CI/CD pipeline parses commit messages to
automatically determine version bumps (via `python-semantic-release`).

Common types:

- `feat:` — A new feature (triggers a minor version bump)
- `fix:` — A bug fix (triggers a patch version bump)
- `docs:` — Documentation only
- `chore:` — Maintenance, tooling, CI/CD
- `refactor:` — Code restructuring without feature or fix

Pushing to `main` triggers automatic version bumping via
`python-semantic-release`. No manual tag creation is needed.

## Agent Instructions

Append discoveries and decisions to `docs/context-tracker.md`.

- Do not commit `.env` files or hardcoded API keys
- New API methods go in the appropriate class (Bus, Train, Taxi, Traffic, Other)
- New endpoints require entries in `constants.py` + method in the class
- Every new API method needs a unit test
- Packaging changes require updating `test/test_sdk_packaging.py`

## Project Structure

```
src/ltasg/
  __init__.py       — public exports + __version__
  api.py            — LTADataMall HTTP client (fetch, fetch_value)
  constants.py      — DEFAULT_BASE_URL, TransportType, LTA_SERVICES, etc.
  traffic.py        — Traffic class (11 APIs)
  other.py          — Other class (bicycle, geospatial, EV)
  transport/
    base.py         — Transport base class with _service_type
    bus.py          — Bus class (arrival, services, routes, stops, PV)
    train.py        — Train class (service alerts, crowd density, PV, maintenance)
    taxi.py         — Taxi class (availability, stands)
test/
  test.py           — E2E tests (quick + slow groups)
  test_unit.py      — Unit tests (mocked fetch)
  test_integration.py — Integration tests (mocked HTTP layer)
  test_sdk_packaging.py — Wheel/sdist integrity tests
```
