# NZ Tax Microsimulation Model

A microsimulation model for New Zealand's tax and benefit system.

This model is designed to be a flexible and extensible tool for researchers, policymakers, and the public to explore the impacts of different tax and benefit policies in New Zealand.

The filename of this document is capitalised as `README.md` so that GitHub
renders it by default when viewing the repository.

## Key Features

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
3. Ongoing maintenance, documentation and feature improvements.
