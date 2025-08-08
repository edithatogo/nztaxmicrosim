# NZ Microsimulation Model

A Python-based microsimulation model for the New Zealand tax and transfer
system. The project re-implements Inland Revenue’s SAS models in an open and
extensible form.

The filename of this document is capitalised as `README.md` so that GitHub
renders it by default when viewing the repository.

## Key Features

- Income tax, Working for Families and FamilyBoost modules
- Modular plug-in simulation pipeline where tax and benefit rules can be
  independently enabled, ordered or substituted
- Rule-based engine for composing Working for Families calculations
- Parameterised policy rules for multiple tax years
- Reporting utilities and sensitivity analysis, including Expected Value of
  Perfect Information (EVPI)
- Optional modules for Paid Parental Leave and Child Support
- Experimental dynamic simulation tools
- Modular simulation pipeline with pluggable rule components
- Script to discover historical tax datasets via the data.govt.nz API
- Rule-based architecture for Working for Families calculations

### Feature Matrix

This document compares the features of the NZ-Microsim library with the original SAS models it is based on, as well as two other popular open-source microsimulation platforms: PolicyEngine and OpenFisca.

| Feature | NZ-Microsim (This Repo) | Original SAS Models | PolicyEngine | OpenFisca |
| --- | --- | --- | --- | --- |
| **Core Focus** | New Zealand tax and transfer system | New Zealand tax and transfer system | Multi-country tax and benefit systems | Generic microsimulation framework ("Legislation as code") |
| **Technology** | Python | SAS | Python | Python |
| **Open Source** | Yes (Apache 2.0 License) | Yes (MIT License) | Yes (AGPL-3.0) | Yes (AGPL-3.0) |
| **Core Engine** | Custom-built | Custom-built | PolicyEngine Core (fork of OpenFisca-Core) | OpenFisca-Core |
| **Modularity** | Modular design with pluggable components | Macro-based (`famsim`) | Highly modular (core engine + country packages) | Highly modular (core engine + country packages) |
| **Country Coverage** | New Zealand only | New Zealand only | US, UK, Canada | France, Spain, Senegal, and others |
| **Web Interface** | No | No | Yes (React-based web app) | Yes (via country packages) |
| **API** | No | No | Yes (REST API) | Yes (REST API) |
| **Parameterisation** | JSON files per tax year | Hardcoded in macros, with some input parameters | YAML files | YAML files |
| **Key Features** | - Income Tax<br>- Working for Families (WFF)<br>- FamilyBoost<br>- IETC<br>- RWT<br>- Superannuation<br>- Reporting & Sensitivity Analysis | - Income Tax<br>- Working for Families (WFF) | - Detailed tax and benefit calculations for each country<br>- Microdata generation<br>- Extensible with new policies | - Core calculus engine<br>- Domain-specific language for policy rules<br>- Handles complex dependencies between variables |
| **Extensibility** | Designed to be extensible | Limited | Designed to be extensible through new country packages or policies | Designed to be extensible through new country packages or policies |
| **Tax Year Coverage** | 2005-2025 | Not specified | Varies by country | Varies by country |
| **Community** | Small, focused on this project | Internal to Inland Revenue | Active community | Active community |

| Feature | Module | Release Status |
| --- | --- | --- |
| Income tax calculations | Income Tax | Core |
| Working for Families | Working for Families | Core |
| FamilyBoost | FamilyBoost | Core |
| Paid Parental Leave | Paid Parental Leave | Optional |
| Child Support | Child Support | Optional |
| Policy rules for multiple tax years | Parameterised Policy Rules | Core |
| Reporting and EVPI analysis | Reporting & Sensitivity | Core |
| Dynamic simulation tools | Dynamic Simulation | Experimental |
| Historical tax dataset discovery | Data.govt.nz API Script | Experimental |


## Quick Start

### Installation

Install the core dependencies:

```bash
make install
```

For development work:

```bash
pip install -e .
```

### Running an Example

Load policy parameters and compute income tax using the convenience class:

```python
from src.tax_calculator import TaxCalculator

calc = TaxCalculator.from_year("2024-2025")
tax = calc.income_tax(50_000)
```

Or execute the example script:

```bash
make run-example
```

## Project Structure

- `src/` – core Python source code and parameter files
- `examples/` – scripts demonstrating how to use the model
- `docs/` – detailed documentation, licences and contribution guides
- `tests/` – unit tests
- `Makefile` – common development tasks
- `pyproject.toml` – dependency and tooling configuration

## Development

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

Report security vulnerabilities responsibly via
[docs/SECURITY.md](docs/SECURITY.md).

## Contributing

Contributions are welcome! See
[docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## License

Licensed under the Apache 2.0 License – see [docs/LICENSE](docs/LICENSE).

## Cite Us

If you use this software in your research, cite the project as described in
[docs/CITATION.cff](docs/CITATION.cff).

## Roadmap

1. Achieve parity with the original SAS models for income tax and Working for
   Families.
2. Add behavioural responses, advanced sensitivity analysis and integrations
   with other social policy models.
<<<<<<< HEAD
3. Ongoing maintenance, documentation and feature improvements.
=======
3. Ongoing maintenance, documentation and feature improvements.
>>>>>>> main
