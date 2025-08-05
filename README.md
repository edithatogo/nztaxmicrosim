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

For a detailed comparison with other microsimulation platforms, please see the [Feature Matrix](feature-matrix.md).

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
the `src` directory. These files are loaded into dataclasses via
`load_parameters`, which performs basic type checks and ensures required fields
are present.

`src/`. Loaded parameter sets behave like both objects and mappings, so you can
access groups with attribute or dictionary-style syntax:

```python
params = load_parameters("2024-2025")
rates = params["tax_brackets"]["rates"]
```

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