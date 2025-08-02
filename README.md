# NZ Microsimulation Model

A Python-based microsimulation model for the New Zealand tax and transfer
system. The project re-implements Inland Revenue’s SAS models in an open and
extensible form.

The filename of this document is capitalised as `README.md` so that GitHub
renders it by default when viewing the repository.

## Key Features

- Income tax, Working for Families and FamilyBoost modules
- Parameterised policy rules for multiple tax years
- Reporting utilities and sensitivity analysis, including Expected Value of
  Perfect Information (EVPI)
- Optional modules for Paid Parental Leave and Child Support
- Experimental dynamic simulation tools
- Script to discover historical tax datasets via the data.govt.nz API

### Feature Matrix

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

params = load_parameters("2024-2025")
tax_brackets = params.tax_brackets
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

