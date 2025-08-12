"""
This module provides tools for policy optimisation, starting with parameter scanning.

The main function, `run_parameter_scan`, allows users to run the simulation
across a grid of different policy parameter combinations and evaluate the
results against a set of user-defined metrics. This is the first phase
of the "Policy Optimisation Module" described in the project roadmap.
"""

from typing import Callable, Dict, List, Any
import pandas as pd
from .microsim import load_parameters
from .dynamic_simulation import _run_static_simulation
import copy

def _set_nested_attr(obj: Any, attr_path: str, value: Any):
    """
    Sets a nested attribute on an object using a dot-separated path.

    Example:
        _set_nested_attr(params, "tax_brackets.rates", [0.1, 0.2])
    """
    parts = attr_path.split('.')
    for part in parts[:-1]:
        obj = getattr(obj, part)
    setattr(obj, parts[-1], value)

def run_parameter_scan(
    base_df: pd.DataFrame,
    base_year: str,
    scan_config: Dict[str, Any],
    metrics: Dict[str, Callable[[pd.DataFrame], float]]
) -> pd.DataFrame:
    """
    Runs a parameter scan simulation.

    This function iterates through a list of scenarios defined in `scan_config`.
    For each scenario, it modifies a base set of policy parameters, runs a
    static simulation, and evaluates the results using the provided metric
    functions.

    The `scan_config` should have a "scenarios" key, which is a list of
    dictionaries. Each dictionary must have an "id" and a "parameters"
    dictionary, where keys are dot-separated paths to the parameter to be
    changed.

    Example `scan_config`:
    {
        "scenarios": [
            {
                "id": "scenario_1",
                "parameters": {
                    "tax_brackets.rates": [0.10, 0.18, 0.30, 0.33, 0.39],
                    "ietc.ent": 600
                }
            }
        ]
    }

    Args:
        base_df: The initial population DataFrame.
        base_year: The base year for the simulation.
        scan_config: A dictionary defining the parameter scenarios to scan.
        metrics: A dictionary of metric functions to evaluate for each scenario.
                 The key is the metric name and the value is a function that
                 takes a DataFrame and returns a float.

    Returns:
        A DataFrame summarizing the results of the parameter scan. Each row
        corresponds to a scenario, and columns include the scenario ID and
        the calculated metrics.
    """
    base_params = load_parameters(base_year)

    all_results = []

    if "scenarios" not in scan_config:
        raise ValueError("scan_config must contain a 'scenarios' key.")

    for scenario in scan_config["scenarios"]:
        if "id" not in scenario or "parameters" not in scenario:
            raise ValueError("Each scenario must have 'id' and 'parameters' keys.")

        scenario_id = scenario["id"]
        param_overrides = scenario["parameters"]

        # Create a deep copy of the base parameters to modify for this scenario
        scenario_params = copy.deepcopy(base_params)

        # Apply the parameter overrides
        for param_path, value in param_overrides.items():
            try:
                _set_nested_attr(scenario_params, param_path, value)
            except AttributeError:
                raise AttributeError(f"Invalid parameter path in scenario '{scenario_id}': {param_path}")

        # Run the static simulation with the modified parameters
        result_df = _run_static_simulation(base_df, scenario_params)

        # Calculate the metrics
        scenario_results = {"scenario_id": scenario_id}
        for metric_name, metric_func in metrics.items():
            scenario_results[metric_name] = metric_func(result_df)

        all_results.append(scenario_results)

    return pd.DataFrame(all_results)
