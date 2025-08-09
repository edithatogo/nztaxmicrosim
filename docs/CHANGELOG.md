# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Improved documentation for contributors, including a more open security policy,
  a new development guide, and clearer instructions in the Code of Conduct.

### Added

- Initial project setup.
- Python project structure with `src/` directory.
- `pyproject.toml` for dependency management and project configuration.
- `pytest` for unit testing.
- `ruff` for linting and formatting.
- `pre-commit` hooks for automated code quality checks.
- `LICENSE` file (Apache 2.0 License).
- `CONTRIBUTING.md` with contribution guidelines.
- `CITATION.cff` for citation information.
- Optional modules for Paid Parental Leave and child support modelling.
- All yearly parameter files now include `ppl` and `child_support` sections so
  these modules can be enabled for any simulation year.
- `SECURITY.md` for vulnerability reporting.
- `sas_models/` directory for original SAS model files.
- `docs/` directory for documentation files.
- `docs/external/` for external reference documents (PDFs).
- `.gitignore` updated to include new directories and IDE-specific files.
- Added type hints to `src/microsim.py`, `src/wff_microsim.py`, and `src/wff_microsim_main.py`.
- Added docstrings to `test_microsim.py` and `test_wff_microsim.py`.
- Added `src/py.typed` to indicate type information availability.
- Added `payroll_deductions.py` with KiwiSaver and student loan helper functions.
- Extended parameter files with KiwiSaver contribution and student loan repayment settings.
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
- Added `calculate_evpi` function for computing the Expected Value of Perfect Information from probabilistic sensitivity outputs and corresponding unit tests.
- Added budget impact analysis utilities for comparing baseline and reform scenarios.
- Added wrapper `calculate_budget_impact` in `src.reporting`.
- Added `src/acc_levy.py` with ACC levy and payroll deduction functions.
- New unit tests for ACC levy calculations.
- Added inequality metrics helpers (`lorenz_curve`, `atkinson_index`, `theil_index`).
- Added simple dynamic simulation utilities for iterating policies across years.
