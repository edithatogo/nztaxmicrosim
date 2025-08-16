# NZ Personal Tax Microsimulation Model

[![CI](https://github.com/edithatogo/nztaxmicrosim/actions/workflows/ci.yml/badge.svg)](https://github.com/edithatogo/nztaxmicrosim/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/edithatogo/nztaxmicrosim/graph/badge.svg?token=YOUR_TOKEN_HERE)](https://codecov.io/gh/edithatogo/nztaxmicrosim)
[![PyPI version](https://badge.fury.io/py/nztaxmicrosim.svg)](https://badge.fury.io/py/nztaxmicrosim)
[![Python versions](https://img.shields.io/pypi/pyversions/nztaxmicrosim.svg)](https://pypi.org/project/nztaxmicrosim)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A microsimulation model for New Zealand's tax and benefit system.

This model is designed to be a flexible and extensible tool for researchers, policymakers, and the public to explore the impacts of different tax and benefit policies in New Zealand.

The filename of this document is capitalised as `README.md` so that GitHub
renders it by default when viewing the repository.

## Key Features

For a more detailed breakdown of all features, see [FEATURES.md](FEATURES.md).

- **Comprehensive Rule Coverage:**
  - **Income Tax:** Full progressive income tax brackets.
  - **Levies:** ACC Earner's Levy.
  - **Tax Credits:** Independent Earner Tax Credit (IETC).
  - **Working for Families:** Family Tax Credit (FTC), In-Work Tax Credit (IWTC), Best Start Tax Credit (BSTC), and Minimum Family Tax Credit (MFTC).
  - **Main Benefits:** Jobseeker Support (JSS), Sole Parent Support (SPS), and Supported Living Payment (SLP).
  - **Other Assistance:** Accommodation Supplement, Winter Energy Payment, and NZ Superannuation.
  - **Deductions:** KiwiSaver and Student Loan repayments.
- **Extensive Historical Data:**
  - Parameterised policy rules for tax years from 2005 to 2025.
  - Automatic fallback to historical data, with coverage from 1890 to 2028.
- **Synthetic Population Generation:**
  - Includes the `syspop` tool to generate realistic synthetic populations for simulation.
- **Flexible Simulation Modes:**
  - Supports both **static** (single-year) and **dynamic** (multi-year) simulations.
  - Extensible framework for modeling behavioural responses over time.
- **Modular and Extensible:**
  - A modular plug-in simulation pipeline where tax and benefit rules can be
    independently enabled, ordered or substituted.
- **Advanced Analysis Tools:**
  - Reporting utilities and sensitivity analysis, including Expected Value of
    Perfect Information (EVPI).

### Feature Matrix

For a detailed comparison of this project with other microsimulation models, see the [Feature Comparison](docs/feature_comparison.md).

For a list of the current features and their release status, see the [Module Status](docs/module_status.md).


## Quick Start

### Installation

Install the core dependencies:

```bash
pip install .
```

For development work:

```bash
make install-dev-deps
```

### Running an Example

To run the basic usage example:

```bash
make run-example
```

This will execute the `examples/basic_usage.py` script and write the output to `basic_usage_output.txt`.

Here is a simplified example of how to use the library:

```python
from src.microsim import load_parameters, taxit

# Load parameters for a specific tax year
params = load_parameters("2024-2025")

# Calculate income tax for an individual
income = 50000
tax = taxit(income, params.tax_brackets)

print(f"Income tax for an income of ${income}: ${tax:.2f}")
```

## Project Structure

- `src/` – core Python source code and parameter files
- `examples/` – scripts demonstrating how to use the model
- `docs/` – detailed documentation, licences and contribution guides
- `tests/` – unit tests
- `syspop/` – synthetic population generator
- `scripts/` – utility scripts
- `conf/` and `config/` – configuration files
- `reports/` – output from reporting scripts
- `Makefile` – common development tasks
- `pyproject.toml` – dependency and tooling configuration

## Development

For more detailed development guidelines, see [DEVELOPMENT.md](docs/DEVELOPMENT.md).

### Tests

Install development dependencies:

```bash
make install-dev-deps
```

Run the test suite with [tox](https://tox.wiki/):

```bash
tox
```

### Linting, Type Checking and Security

Run formatting, linting, static type checks and security scans with
[pre-commit](https://pre-commit.com/):

```bash
pre-commit run --all-files
```

Install pre-commit hooks with `pre-commit install` to run these checks
automatically.

## Parameters

Policy rules are stored in JSON files named `parameters_YYYY-YYYY.json` inside
the `src` directory. These files are loaded into Pydantic models via
`load_parameters`, which performs basic type checks and ensures required fields
are present.


## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a history of changes.

## Security

See our security policy in [docs/SECURITY.md](docs/SECURITY.md).

## Contributing

Contributions are welcome! See
[docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## License

Licensed under the Apache 2.0 License – see [docs/LICENSE](docs/LICENSE).

## Cite Us

If you use this software in your research, cite the project as described in
[docs/CITATION.cff](docs/CITATION.cff).

## Roadmap

The project is in a mature state, with most of the core features completed. The current focus is on improving the model's flexibility, optimization capabilities, and architecture.

### In Progress

- **Policy Optimisation Module:** Integrating an optimization library (e.g., Optuna) to intelligently search for optimal policy parameters.
- **Configuration-Driven Pipelines:** Refactoring the simulation to be driven by configuration files (e.g., YAML) to make it more flexible.

### Future Plans

- **Parameter Database:** Migrating policy parameters from JSON files to a structured database (e.g., SQLite).
- **Web API:** Exposing the simulation engine via a web API to make it more accessible to other tools and languages.
- **Enhanced CI/CD:** Improving the CI/CD pipeline with dynamic badges, automated data audits, and performance regression testing.

For more details, see the full [Roadmap](docs/ROADMAP.md).
