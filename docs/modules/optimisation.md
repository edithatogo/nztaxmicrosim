# Policy Optimisation: Parameter Scanning

This document describes the Parameter Scanning tool, which is the first phase of the Policy Optimisation module. This tool allows researchers and policy analysts to efficiently run the microsimulation model across multiple variations of policy parameters and evaluate the results.

## Overview

The core of the tool is the `run_parameter_scan` function located in `src.optimisation`. It is designed to answer questions like:
- "What would be the effect on total tax revenue if we changed the top tax rate?"
- "How does increasing a tax credit affect government expenditure compared to the baseline policy?"

It works by taking a baseline population and a set of policy "scenarios". For each scenario, it adjusts the policy parameters, runs a simulation, and calculates a set of key metrics defined by the user.

## How to Use

Using the tool involves three main steps:
1.  **Prepare a population dataset:** This is a standard pandas DataFrame, the same kind used for single simulation runs.
2.  **Create a YAML configuration file:** This file defines the different policy scenarios you want to test.
3.  **Define metric functions:** These are Python functions that calculate the specific outcomes you are interested in (e.g., revenue, inequality).

### Example Script

An example script is provided in `examples/run_parameter_scan.py`. It demonstrates the full workflow. To run it, you can execute:
```bash
python examples/run_parameter_scan.py
```

### 1. The Configuration File

The scenarios are defined in a YAML file. The file must have a top-level key called `scenarios`, which contains a list of individual scenario configurations.

Each scenario needs:
- `id`: A unique string to identify the scenario in the results.
- `description`: A brief explanation of what the scenario does.
- `parameters`: A dictionary where keys are the parameters to change, and values are the new values.

Parameter keys are **dot-separated paths** that correspond to the structure of the `Parameters` model in `src.parameters`.

**Example: `examples/scan_config.yaml`**
```yaml
scenarios:
  - id: "baseline"
    description: "The current policy settings for 2024-2025."
    parameters:
      # No overrides, use the default parameters for the base year.
      {}

  - id: "higher_top_tax_rate"
    description: "Increase the top tax rate from 39% to 42%."
    parameters:
      tax_brackets.rates: [0.105, 0.175, 0.30, 0.33, 0.42]

  - id: "increase_ietc"
    description: "Increase the Independent Earner Tax Credit entitlement by 20%."
    parameters:
      ietc.ent: 624 # Original is 520
```

### 2. Defining Metric Functions

You can measure any outcome from a simulation by defining a "metric function". This is a Python function that accepts a pandas DataFrame (the output of a simulation) and returns a single number.

**Example from the script:**
```python
def total_tax_revenue(df: pd.DataFrame) -> float:
    """Calculates the total income tax paid by the population."""
    return df["tax_liability"].sum()

def total_wff_paid(df: pd.DataFrame) -> float:
    """Calculates the total Working for Families credits paid."""
    wff_columns = ["FTCcalc", "IWTCcalc", "BSTCcalc", "MFTCcalc"]
    existing_cols = [col for col in wff_columns if col in df.columns]
    return df[existing_cols].sum().sum()

# These are then passed to the scanner in a dictionary:
metrics_to_run = {
    "Total Tax Revenue": total_tax_revenue,
    "Total WFF Paid": total_wff_paid
}
```

## Function Reference

`run_parameter_scan(base_df, base_year, scan_config, metrics)`

- **`base_df`**: The initial population DataFrame.
- **`base_year`**: The base year for the simulation (e.g., "2024-2025"). The tool will load the default parameters for this year before applying any scenario overrides.
- **`scan_config`**: A dictionary loaded from your YAML configuration file.
- **`metrics`**: A dictionary mapping metric names (strings) to your metric functions.

The function returns a pandas DataFrame where each row contains the results for one scenario, making it easy to compare the impacts of different policy choices.

---

## Phase 2: Advanced Policy Optimisation with Optuna

Building on the parameter scanning tool, the advanced policy optimisation feature uses the `Optuna` library to intelligently search for optimal policy parameters. Instead of testing a pre-defined grid of scenarios, this tool explores a continuous search space to find parameter combinations that maximize or minimize a specific objective function.

### How it Works

The core of this feature is the `run_policy_optimisation` function. It wraps the simulation logic in an "objective function" that Optuna repeatedly calls with different parameter values. Optuna's samplers use the history of previous results to guide the search towards more promising areas of the parameter space.

### How to Use

The workflow is similar to the parameter scanner, but the configuration file is different.

**Example Script:**
An example is provided in `examples/run_policy_optimisation.py`.
```bash
python examples/run_policy_optimisation.py
```

### 1. The Optimisation Configuration File

The study is defined in a YAML file. It has three main sections: `objective`, `n_trials`, and `search_space`.

- **`objective`**: Defines the goal of the study.
  - `name`: The metric to be optimized. This must correspond to a key in the `metrics` dictionary you provide.
  - `direction`: Can be `"maximize"` or `"minimize"`.
- **`n_trials`**: The total number of simulations the optimiser will run.
- **`search_space`**: A list of parameters to vary. Each entry defines:
  - `name`: A unique name for the parameter in the study.
  - `path`: The dot-separated path to the parameter in the `Parameters` model.
  - `type`: The type of value to search for (`float`, `int`, or `categorical`).
  - The range of values (`low` and `high` for `float`/`int`, or `choices` for `categorical`).

**Example: `examples/opt_config.yaml`**
```yaml
objective:
  name: "total_tax_revenue"
  direction: "maximize"

n_trials: 50

search_space:
  - name: "top_tax_rate"
    path: "tax_brackets.rates.4"
    type: "float"
    low: 0.38
    high: 0.45
  - name: "ietc_entitlement"
    path: "ietc.ent"
    type: "int"
    low: 520
    high: 700
```

### 2. Interpreting the Results

The `run_policy_optimisation` function returns a completed Optuna `study` object. This object contains a wealth of information about the optimisation process. The example script shows how to access the most important results:

- `study.best_trial`: The trial that resulted in the best objective value.
- `study.best_params`: A dictionary of the parameter values that yielded the best result.
- `study.best_value`: The best objective score achieved.

You can also access the `user_attrs` of the best trial to see the values of all other metrics for that trial, which is useful for understanding trade-offs.

For more advanced analysis, Optuna provides powerful visualization tools (e.g., `optuna.visualization.plot_optimization_history`) that can be used with the returned `study` object.

