# Copilot Instructions for the NZ Tax Microsimulation Model

This document provides instructions for Copilot to work efficiently with this repository. Please follow these guidelines to ensure that your contributions are consistent with the project's standards and practices.

## High-Level Details

### Repository Summary

This repository contains a Python-based microsimulation model for the New Zealand tax and benefit system. It is designed to be a flexible and extensible tool for researchers, policymakers, and the public to explore the impacts of different tax and benefit policies in New Zealand.

### Repository Information

- **Size:** Medium
- **Project Type:** Python application
- **Languages:** Python
- **Frameworks and Libraries:** `pandas`, `numpy`, `pydantic`, `matplotlib`, `seaborn`, `joblib`, `scipy`, `tabulate`, `requests`, `pyyaml`, `pytest`, `ruff`, `mypy`, `tox`.
- **Target Runtimes:** Python 3.9, 3.10, 3.11

## Build Instructions

### Bootstrap

To set up the development environment, you need to install the project's dependencies.

1.  **Install core dependencies:**
    ```bash
    make install
    ```
    or
    ```bash
    pip install .
    ```

2.  **Install development dependencies:**
    ```bash
    make install-dev-deps
    ```
    or
    ```bash
    pip install -e .
    pip install -r requirements-dev.txt
    ```

### Build

This is a Python project, so there is no explicit build step. Once the dependencies are installed, the project is ready to run.

### Test

The project uses `tox` to run the test suite. The tests are located in the `tests/` directory.

To run the tests, execute the following command:

```bash
tox
```

This will run the tests against the Python versions specified in `tox.ini`. The CI pipeline runs tests on Python 3.9, 3.10, and 3.11.

To run the tests with coverage, you can use the `coverage` make target:

```bash
make coverage
```

### Run

To run the example scripts, use the `make` commands:

-   Run the basic usage example:
    ```bash
    make run-example
    ```
-   Run the microsimulation comparison example:
    ```bash
    make run-microsim-comparison
    ```
-   Generate reports:
    ```bash
    make generate-reports
    ```

### Lint and Format

The project uses `ruff` for linting and formatting.

-   **Check for linting errors and formatting issues:**
    ```bash
    make lint
    ```
-   **Format the code:**
    ```bash
    make format
    ```

### Type Checking

The project uses `mypy` for static type checking.

-   **Run mypy:**
    ```bash
    mypy .
    ```

### Pre-commit Hooks

The project uses pre-commit hooks to run linting, formatting, and type checking automatically before each commit. To install the hooks, run:

```bash
pre-commit install
```

To run the hooks on all files, use:

```bash
pre-commit run --all-files
```

## Project Layout

### Architectural Elements

-   `src/`: Contains the core Python source code and parameter files.
    -   `src/parameters_YYYY-YYYY.json`: Policy rules for each tax year.
    -   `src/tax_calculator.py`: Main class for tax calculations.
    -   `src/microsim.py`: Core microsimulation engine.
-   `tests/`: Contains the unit tests.
-   `examples/`: Contains scripts demonstrating how to use the model.
-   `docs/`: Contains detailed documentation, licenses, and contribution guides.
-   `Makefile`: Contains common development tasks.
-   `pyproject.toml`: Contains dependency and tooling configuration.
-   `tox.ini`: Contains test environment configuration.
-   `.pre-commit-config.yaml`: Contains pre-commit hook configuration.
-   `.github/workflows/ci.yml`: Contains the CI pipeline configuration.

### Validation

-   **CI Pipeline:** The CI pipeline is defined in `.github/workflows/ci.yml`. It runs linting, formatting, type checking, and tests on all pull requests and pushes to the `main` branch.
-   **Pre-commit Hooks:** The pre-commit hooks defined in `.pre-commit-config.yaml` run checks before each commit.
-   **Tests:** The test suite in the `tests/` directory provides validation for the model's calculations.

### Dependencies

The project's dependencies are listed in `pyproject.toml` and `requirements-dev.txt`.

## Final Instructions

Please trust these instructions. Only perform a search if the information in these instructions is incomplete or found to be in error.
