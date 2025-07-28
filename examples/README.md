# Examples

This directory contains example scripts demonstrating how to use the NZ Microsimulation Model.

## Contents:

*   `basic_usage.py`: A simple script demonstrating how to import and use the
    `taxit` function from the `src/microsim.py` module.
*   `generate_reports.py`: Creates publication‑ready plots and tables from
    microsimulation output. Run this after generating results with the synthetic
    population scripts.
*   `run_microsim_comparison.py`: Generates a synthetic population (scaled down
    for quick tests) and runs the microsimulation for multiple parameter files,
    saving one results file per year.
*   `run_microsim_with_artificial_population.py`: Builds a small artificial
    population inside the script and runs the model to demonstrate the required
    input structure.
*   `run_microsim_with_synthetic_population.py`: Uses the `syspop` package to
    create a synthetic population and then runs the microsimulation for the
    specified years.
*   `run_sensitivity_analysis.py`: Performs deterministic and probabilistic
    sensitivity analyses on key parameters and writes plots to the `reports`
    directory.
*   `run_validation.py`: Runs the WFF microsimulation with all available
    parameter files and writes a Markdown summary to `docs/validation_report.md`.
*   `run_validation_with_dummy_data.py`: Demonstrates validation and execution
    using a small hard‑coded dataset.

### Running the examples

Execute any script from the project root, for example:

```bash
python examples/run_microsim_with_synthetic_population.py --param_files src/parameters_2024-2025.json
```

Results and reports will be written inside the `examples` directory.
