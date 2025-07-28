# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial project setup.
- Python project structure with `src/` directory.
- `pyproject.toml` for dependency management and project configuration.
- `pytest` for unit testing.
- `ruff` for linting and formatting.
- `pre-commit` hooks for automated code quality checks.
- `LICENSE` file (MIT License).
- `CONTRIBUTING.md` with contribution guidelines.
- `CITATION.cff` for citation information.
- `SECURITY.md` for vulnerability reporting.
- `sas_models/` directory for original SAS model files.
- `docs/` directory for documentation files.
- `docs/external/` for external reference documents (PDFs).
- `.gitignore` updated to include new directories and IDE-specific files.
- Added type hints to `src/microsim.py`, `src/wff_microsim.py`, and `src/wff_microsim_main.py`.
- Added docstrings to `test_microsim.py` and `test_wff_microsim.py`.
- Added `src/py.typed` to indicate type information availability.
- Added `README.md` files to `src/`, `sas_models/`, `docs/`, `examples/`, `tests/`, and `docs/external/` directories.
- Moved test files to `tests/` directory and updated `pyproject.toml` accordingly.
- Added `requirements-dev.txt` for development dependencies and updated `Makefile` to use it.
- Refined `CITATION.cff` to use generic project information.
- Moved `CITATION.cff` to `docs/` directory.
- Moved `CONTRIBUTING.md` to `docs/` directory.
- Moved `SECURITY.md` to `docs/` directory.
- Added `install` target to `Makefile` and updated `README.md` with installation instructions.
- Added `run-example` target to `Makefile` and updated `README.md` with instructions on how to run the example.
- Added `.github/CODEOWNERS` file and a corresponding `README.md` to the `.github/` directory.
- Moved `LICENSE` file to `docs/` directory.
- Added inequality metrics helpers (`lorenz_curve`, `atkinson_index`, `theil_index`).

