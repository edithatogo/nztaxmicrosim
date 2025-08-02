# NZ Microsimulation Model

A Python-based microsimulation model for the New Zealand tax and transfer
system. The project re-implements Inland Revenue’s SAS models in an open and
extensible form.

## Key Features

- Income tax, Working for Families and FamilyBoost modules
- Parameterised policy rules for multiple tax years
- Reporting utilities and sensitivity analysis, including Expected Value of
  Perfect Information (EVPI)
- Optional modules for Paid Parental Leave and Child Support
- Experimental dynamic simulation tools
- Script to discover historical tax datasets via the data.govt.nz API

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

tax_calc = TaxCalculator.from_year("2024-2025")
tax = tax_calc.income_tax(50_000)
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
`src/`. Use `TaxCalculator.from_year()` to load them for a given tax year.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a history of changes.

## Security

Report security vulnerabilities responsibly via
[docs/SECURITY.md](docs/SECURITY.md).

## Contributing

Contributions are welcome! See
[docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## License

Licensed under the MIT License – see [docs/LICENSE](docs/LICENSE).

## Cite Us

If you use this software in your research, cite the project as described in
[docs/CITATION.cff](docs/CITATION.cff).

## Roadmap

1. Achieve parity with the original SAS models for income tax and Working for
   Families.
2. Add behavioural responses, advanced sensitivity analysis and integrations
   with other social policy models.
3. Ongoing maintenance, documentation and feature improvements.

