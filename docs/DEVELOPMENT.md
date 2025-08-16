This repository aims to produce a microsimulator for New Zealand tax settings capable of both static and dynamic analysis to evaluate budget impact, personal income outcomes, equity, value-of-information, and related metrics.

- Before committing, run `ruff check .` and `ruff format --check .` to ensure code style.
- Ensure all tests pass by running `pytest`.
- Update documentation (`README.md`, `ROADMAP.md`, `TODO.md`) when features change.
- Use clear, descriptive commit messages.

## Continuous Integration

This project includes scripts to help automate testing and quality checks.

### Running All Checks

The `scripts/ci.sh` script is the main entry point for running all continuous integration checks. This includes running the full test suite with `tox` and performing a data integrity audit.

```bash
./scripts/ci.sh
```

This script is designed to be run in a CI environment (like GitHub Actions), but can also be run locally to ensure everything is correct before pushing changes.

### Data Audit

The `scripts/audit_historical_data.py` script checks the historical parameter database for correctness and consistency. It ensures that no policies exist in years before they were officially introduced, and that there are no unexpected gaps in the data.

### Performance Profiling

The `scripts/run_profiling.sh` script runs the test suite with performance profiling enabled. It saves the profiling data to a new file in the `prof/` directory. This is useful for tracking performance over time and identifying potential regressions.

```bash
./scripts/run_profiling.sh
```
