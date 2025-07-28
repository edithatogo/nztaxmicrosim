# Examples

This directory contains example scripts demonstrating how to use the NZ Microsimulation Model.

## Contents

* `basic_usage.py`: Shows basic use of functions like `taxit` and `famsim` on a small dataset. Run with `python examples/basic_usage.py`.
* `generate_reports.py`: Creates publication-ready plots and tables from microsimulation results. Run after generating data, for example:
  `python examples/generate_reports.py --param_files src/parameters_2024-2025.json`.
* `run_microsim_comparison.py`: Builds a small synthetic population and runs the model for multiple parameter files. Example:
  `python examples/run_microsim_comparison.py --param_files src/parameters_2024-2025.json src/parameters_2025-2026.json --population_scale 0.1`.
* `run_microsim_with_artificial_population.py`: Creates an artificial population within the script and runs the model. Run with `python examples/run_microsim_with_artificial_population.py`.
* `run_microsim_with_synthetic_population.py`: Uses the `syspop` package to create a synthetic population and run the model for the specified years. Example:
  `python examples/run_microsim_with_synthetic_population.py --param_files src/parameters_2024-2025.json`.
* `run_sensitivity_analysis.py`: Performs deterministic and probabilistic sensitivity analyses on key parameters and writes plots to `examples/reports`. Run with `python examples/run_sensitivity_analysis.py`.
* `run_validation.py`: Runs the WFF microsimulation with all available parameter files and writes a Markdown summary to `docs/validation_report.md`. Execute `python examples/run_validation.py`.
* `run_validation_with_dummy_data.py`: Demonstrates validation and execution using a small hard-coded dataset. Run `python examples/run_validation_with_dummy_data.py`.

### Running the examples

Execute scripts from the project root. Results and reports will be written inside the `examples` directory.
