# Copilot Instructions for the NZ Personal Tax Microsimulation Model

This document provides instructions for a coding agent to work efficiently with this repository. Please follow these instructions to ensure your contributions align with the project's standards and practices.

## High-Level Details

### Repository Summary

This repository contains a microsimulation model for New Zealand's tax and benefit system. It is a Python-based tool for researchers, policymakers, and the public to explore the impacts of different tax and benefit policies. The model supports both static (single-year) and dynamic (multi-year) simulations and includes a wide range of tax and benefit rules, with historical data from 2005 to 2025.

### Repository Information

- **Languages:** Python
- **Primary Libraries:** Pandas, NumPy, Pydantic, Optuna, PyYAML, FastAPI
- **Project Type:** Scientific computing/data analysis library, with a command-line interface and a web API.
- **Target Runtimes:** Python 3.9, 3.10, 3.11

## Build Instructions

This project uses `make` for common tasks and `tox` for testing across multiple Python versions.

### 1. Bootstrap / Installation

**Always start by creating and activating a virtual environment.**

To install the project and its core dependencies, run:
```bash
make install
```

For development, which includes all testing and linting dependencies, use:
```bash
make install-dev-deps
```
This command installs the project in editable mode and pulls dependencies from `requirements-dev.txt`.

### 2. Running Tests

The primary method for running tests is with `tox`, which will test against Python 3.9, 3.10, and 3.11, as defined in `tox.ini`. This is the same command run in the CI pipeline.

**Always run `tox` before submitting a change.**
```bash
tox
```
This command may take a few minutes to complete the first time as it sets up virtual environments for each Python version.

Alternatively, you can run tests for your current Python environment using `pytest`:
```bash
make test
```

To get a coverage report:
```bash
make coverage
```

### 3. Linting and Formatting

This project uses `ruff` for both linting and formatting, and `mypy` for type checking. The CI pipeline will fail if there are any linting, formatting, or type errors.

To check for linting and formatting issues, run:
```bash
make lint
```

To automatically fix formatting issues, run:
```bash
make format
```

It is highly recommended to set up pre-commit hooks to automate this process. After running `make install-dev-deps` (which installs `pre-commit`), run:
```bash
pre-commit install
```

### 4. Running the Application and Examples

You can run the basic example script with:
```bash
make run-example
```

Other examples can be run directly with Python, for example:
```bash
python examples/run_pipeline_from_config.py
```

## Project Layout

### Architectural Overview

- `src/`: The core Python source code for the microsimulation model.
  - `src/parameters.py`: Pydantic models for policy parameters.
  - `src/tax_calculator.py`: Core tax calculation logic.
  - `src/pipeline.py`: The modular simulation pipeline.
  - `src/benefit_rules.py`, `src/tax_rules.py`, `src/wff_rules.py`: Modules containing the definitions for individual simulation rules.
  - `src/api/`: Source code for the FastAPI web application.
  - `src/data/`: Data files used by the model, including the `parameters.db` SQLite database.
- `tests/`: Unit and integration tests.
- `examples/`: Example scripts demonstrating how to use the library.
- `docs/`: Project documentation.
- `conf/`: Configuration files for the simulation pipeline.

### Key Configuration Files

- `pyproject.toml`: Defines project dependencies, build system, and tool configurations (pytest, ruff, mypy).
- `tox.ini`: Configuration for `tox`, specifying the Python versions to test against.
- `.pre-commit-config.yaml`: Defines the pre-commit hooks for automated linting and formatting.
- `Makefile`: Contains shortcuts for common development tasks like installation, testing, and linting.
- `.github/workflows/ci.yml`: Defines the Continuous Integration (CI) pipeline run on GitHub Actions. It includes jobs for linting and testing across multiple Python versions.

### Validation and CI

Before committing code, ensure that:
1.  All tests pass by running `tox`.
2.  The code is correctly formatted and linted by running `make lint`.

The CI pipeline (`.github/workflows/ci.yml`) will automatically run these checks on every push and pull request to the `main` branch. Your changes must pass CI before they can be merged.

---

**Please trust these instructions.** Only resort to searching the codebase if these instructions are incomplete or incorrect for your task. By following these guidelines, you will help ensure the quality and consistency of the codebase.
