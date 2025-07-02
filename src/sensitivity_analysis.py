from typing import Any, Callable, Dict, List

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

from src.microsim import load_parameters


def _get_nested(d, path):
    """Gets a value from a nested dictionary using a dot-separated path."""
    keys = path.split(".")
    for key in keys:
        if isinstance(d, list):
            d = d[int(key)]
        else:
            d = d[key]
    return d


def _set_nested(d, path, value):
    """Sets a value in a nested dictionary using a dot-separated path."""
    keys = path.split(".")
    d_ref = d
    for key in keys[:-1]:
        if isinstance(d_ref, list):
            d_ref = d_ref[int(key)]
        else:
            d_ref = d_ref[key]
    if isinstance(d_ref, list):
        d_ref[int(keys[-1])] = value
    else:
        d_ref[keys[-1]] = value


def run_deterministic_analysis(
    baseline_params: Dict[str, Any],
    params_to_vary: List[str],
    pct_change: float,
    population_df: pd.DataFrame,
    output_metric_func: Callable[[pd.DataFrame], float],
    wff_runner: Callable,
    tax_runner: Callable,
) -> pd.DataFrame:
    """
    Performs a deterministic sensitivity analysis on the microsimulation model.

    Args:
        baseline_params (Dict[str, Any]): The baseline set of parameters.
        params_to_vary (List[str]): A list of parameter names to vary.
        pct_change (float): The percentage change to apply to each parameter.
        population_df (pd.DataFrame): The population data to run the simulation on.
        output_metric_func (Callable[[pd.DataFrame], float]): A function that takes a
            simulation result DataFrame and returns a single output metric.
        wff_runner (Callable): The function that runs the WFF simulation.
        tax_runner (Callable): The function that runs the tax simulation.

    Returns:
        pd.DataFrame: A DataFrame with the results of the sensitivity analysis.
    """

    def _run_simulation(params):
        """Helper function to run a single simulation."""
        # Run tax simulation
        tax_runner(population_df["familyinc"], params["tax_brackets"]["rates"], params["tax_brackets"]["thresholds"])

        # Run WFF simulation
        wff_results = wff_runner(
            population_df.copy(),
            params["wff"],
            0.0,  # wagegwt
            365,  # daysinperiod
        )
        return output_metric_func(wff_results)

    tasks = []
    for param_path in params_to_vary:
        # Create deep copies of the baseline parameters
        params_low = pd.DataFrame([baseline_params]).to_dict(orient="records")[0]
        params_high = pd.DataFrame([baseline_params]).to_dict(orient="records")[0]

        # Get the current value
        current_value = _get_nested(params_low, param_path)

        # Calculate the new values
        low_value = current_value * (1 - pct_change)
        high_value = current_value * (1 + pct_change)

        # Update the parameters
        _set_nested(params_low, param_path, low_value)
        _set_nested(params_high, param_path, high_value)

        tasks.append(delayed(_run_simulation)(params_low))
        tasks.append(delayed(_run_simulation)(params_high))

    # Run simulations in parallel
    results = Parallel(n_jobs=-1)(tasks)

    # Process results
    output_data = []
    baseline_result = _run_simulation(baseline_params)
    for i, param_path in enumerate(params_to_vary):
        low_result = results[i * 2]
        high_result = results[i * 2 + 1]
        output_data.append(
            {
                "parameter": param_path,
                "low_value": low_result,
                "high_value": high_result,
                "baseline": baseline_result,
                "impact": high_result - low_result,
            }
        )

    return pd.DataFrame(output_data)


def run_probabilistic_analysis(
    param_distributions: Dict[str, Dict[str, Any]],
    num_samples: int,
    population_df: pd.DataFrame,
    output_metric_func: Callable[[pd.DataFrame], float],
    wff_runner: Callable,
    tax_runner: Callable,
) -> np.ndarray:
    """
    Performs a probabilistic sensitivity analysis on the microsimulation model.

    Args:
        param_distributions (Dict[str, Dict[str, Any]]): A dictionary defining the
            probability distribution for each parameter to be varied.
        num_samples (int): The number of samples to generate.
        population_df (pd.DataFrame): The population data to run the simulation on.
        output_metric_func (Callable[[pd.DataFrame], float]): A function that takes a
            simulation result DataFrame and returns a single output metric.
        wff_runner (Callable): The function that runs the WFF simulation.
        tax_runner (Callable): The function that runs the tax simulation.

    Returns:
        np.ndarray: An array containing the results from all the simulations.
    """
    from scipy.stats import norm, qmc, uniform

    # Create the sampler
    sampler = qmc.LatinHypercube(d=len(param_distributions))
    sample = sampler.random(n=num_samples)

    # Create the parameter sets
    param_sets = []
    for i in range(num_samples):
        params = {}
        for j, (param_path, dist_info) in enumerate(param_distributions.items()):
            if dist_info["dist"] == "norm":
                value = norm.ppf(sample[i][j], loc=dist_info["loc"], scale=dist_info["scale"])
            elif dist_info["dist"] == "uniform":
                value = uniform.ppf(sample[i][j], loc=dist_info["loc"], scale=dist_info["scale"])
            else:
                raise ValueError(f"Unsupported distribution: {dist_info['dist']}")

            # This is a simplified way to create the nested structure.
            # It might need to be made more robust for more complex cases.
            keys = param_path.split(".")
            d = params
            for key in keys[:-1]:
                d = d.setdefault(key, {})
            d[keys[-1]] = value
        param_sets.append(params)

    def _run_simulation(params):
        """Helper function to run a single simulation."""
        # Load baseline parameters and update with the sampled values
        baseline_params = load_parameters("2023-2024")  # A bit of a hack
        for key, value in params.items():
            if key in baseline_params:
                baseline_params[key].update(value)

        # Run tax simulation
        tax_runner(
            population_df["familyinc"],
            baseline_params["tax_brackets"]["rates"],
            baseline_params["tax_brackets"]["thresholds"],
        )

        # Run WFF simulation
        wff_results = wff_runner(
            population_df.copy(),
            baseline_params["wff"],
            0.0,  # wagegwt
            365,  # daysinperiod
        )
        return output_metric_func(wff_results)

    # Run simulations in parallel
    results = Parallel(n_jobs=-1)(delayed(_run_simulation)(params) for params in param_sets)

    return np.array(results)
