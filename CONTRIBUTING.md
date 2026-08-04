# Contributing to ltasg

Thank you for helping improve `ltasg`. Please open an issue before substantial changes so the intended API and compatibility impact can be discussed.

## Development setup

```sh
git clone https://github.com/ashe0047/ltasg.git
cd ltasg
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
pre-commit install
```

The project requires Python 3.12 or newer. Live LTA DataMall tests require an API key in `LTA_API_KEY`; ordinary unit and integration tests do not require credentials.

## Checks before opening a pull request

```sh
python -m pytest test/ -v --timeout=30
ruff check src/ltasg/ test/
ruff format --check src/ltasg/ test/
mypy src/ltasg/
pre-commit run --all-files
python -m build
twine check dist/*
```

Add or update tests for behavior changes. Keep tests deterministic and do not commit API keys, `.env` files, build artifacts, or generated credentials.

## Pull requests

- Use a focused branch and explain the user-visible behavior or maintenance reason.
- Link the relevant issue when one exists.
- Include test and documentation updates with code changes.
- Keep the pull request description complete using the project template.
- Resolve review conversations before requesting final review.

## Commit and release conventions

Use [Conventional Commits](https://www.conventionalcommits.org/), for example `feat: add ...`, `fix: handle ...`, or `docs: clarify ...`. Semantic Release determines version changes from commits merged to `main`; maintainers handle the release workflow and PyPI publication.

## API additions

New DataMall endpoints should have a constant, a public client method, unit coverage, and documentation. Confirm endpoint names and response behavior against the [official LTA DataMall API User Guide](https://datamall.lta.gov.sg/content/dam/datamall/datasets/LTA_DataMall_API_User_Guide.pdf?ref=public_apis).
