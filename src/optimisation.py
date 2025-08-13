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
import optuna

def _set_nested_attr(obj: Any, attr_path: str, value: Any):
    """
    Sets a nested attribute on an object using a dot-separated path.
    Handles nested objects and list indices.

    Example:
        _set_nested_attr(params, "tax_brackets.rates.4", 0.45)
    """
    parts = attr_path.split('.')
    for i, part in enumerate(parts[:-1]):
        if part.isdigit():
            obj = obj[int(part)]
        else:
            obj = getattr(obj, part)

    last_part = parts[-1]
    if last_part.isdigit():
        obj[int(last_part)] = value
    else:
        setattr(obj, last_part, value)

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


def run_policy_optimisation(
    base_df: pd.DataFrame,
    base_year: str,
    opt_config: Dict[str, Any],
    metrics: Dict[str, Callable[[pd.DataFrame], float]]
) -> optuna.study.Study:
    """
    Runs a policy optimisation using Optuna.

    Args:
        base_df: The initial population DataFrame.
        base_year: The base year for the simulation.
        opt_config: A dictionary defining the optimisation study.
        metrics: A dictionary of metric functions to evaluate.

    Returns:
        The completed Optuna study object.
    """
    base_params = load_parameters(base_year)

    def objective(trial: optuna.trial.Trial) -> float:
        scenario_params = copy.deepcopy(base_params)

        # Suggest new parameter values based on the search space
        for param_config in opt_config["search_space"]:
            name = param_config["name"]
            path = param_config["path"]
            param_type = param_config["type"]

            if param_type == "float":
                value = trial.suggest_float(name, param_config["low"], param_config["high"])
            elif param_type == "int":
                value = trial.suggest_int(name, param_config["low"], param_config["high"])
            elif param_type == "categorical":
                value = trial.suggest_categorical(name, param_config["choices"])
            else:
                raise ValueError(f"Unsupported parameter type: {param_type}")

            _set_nested_attr(scenario_params, path, value)

        # Run simulation and calculate all metrics
        result_df = _run_static_simulation(base_df, scenario_params)

        all_metric_results = {}
        for metric_name, metric_func in metrics.items():
            all_metric_results[metric_name] = metric_func(result_df)

        # Store all metrics for later analysis
        trial.set_user_attr("metrics", all_metric_results)

        # Return the specific metric we are optimising for
        objective_metric_name = opt_config["objective"]["name"]
        if objective_metric_name not in all_metric_results:
            raise ValueError(f"Objective metric '{objective_metric_name}' not found in calculated metrics.")

        return all_metric_results[objective_metric_name]

    study = optuna.create_study(direction=opt_config["objective"]["direction"])
    study.optimize(objective, n_trials=opt_config.get("n_trials", 100))

<<<<<<< HEAD
    return study
=======
    return study
>>>>>>> main
