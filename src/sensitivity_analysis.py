from typing import Any, Callable, Dict, List
import copy

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

from src.microsim import load_parameters


def _get_nested(d: Dict[str, Any], path: str) -> Any:
    """Get a value from a nested dictionary using a dot-separated path.

    This function navigates through a nested dictionary `d` using a `path`
    string (e.g., "key1.key2.0.key3") to retrieve a value. The path can
    contain both dictionary keys and list indices.

    Args:
        d: The nested dictionary or list to access.
        path: A string of dot-separated keys and indices.

    Returns:
        The value at the specified path.
    """
    keys = path.split(".")
    for key in keys:
        if isinstance(d, list):
            d = d[int(key)]
        else:
            d = d[key]
    return d


def _set_nested(d: Dict[str, Any], path: str, value: Any) -> None:
    """Set a value in a nested dictionary using a dot-separated path.

    This function navigates through a nested dictionary `d` using a `path`
    string (e.g., "key1.key2.0.key3") to set a `value` at that location.
    The path can contain both dictionary keys and list indices.

    Args:
        d: The nested dictionary or list to modify.
        path: A string of dot-separated keys and indices.
        value: The value to set at the specified path.
    """
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
    output_metric_funcs: Dict[str, Callable[[pd.DataFrame, pd.DataFrame], float]],
    wff_runner: Callable,
    tax_runner: Callable,
    n_jobs: int = -1,
) -> Dict[str, pd.DataFrame]:
    """
    Perform a deterministic sensitivity analysis on the microsimulation model.

    This analysis involves systematically changing one parameter at a time by a
    fixed percentage, and observing the impact on various output metrics. This
    is useful for understanding which parameters have the most influence on the
    model's results.

    Args:
        baseline_params: The baseline set of parameters for the simulation.
        params_to_vary: A list of parameter names to be varied in the analysis.
        pct_change: The percentage change to apply to each parameter (e.g.,
            0.1 for 10%).
        population_df: The population data to run the simulation on.
        output_metric_funcs: A dictionary of functions that each take a tax
            result and a WFF result DataFrame and return a single output
            metric.
        wff_runner: The function that runs the Working for Families simulation.
        tax_runner: The function that runs the tax simulation.
        n_jobs: The number of jobs to run in parallel. Defaults to -1, which
            uses all available CPU cores.

    Returns:
        A dictionary where keys are metric names and values are DataFrames
        containing the sensitivity analysis results for that metric.
    """

    def _run_simulation(params):
        """Helper function to run a single simulation and calculate all metrics."""
        tax_df = pd.DataFrame(
            {
                "tax": population_df["familyinc"].apply(
                    tax_runner,
                    args=(params["tax_brackets"]["rates"], params["tax_brackets"]["thresholds"]),
                )
            }
        )
        wff_df = wff_runner(
            population_df.copy(),
            params["wff"],
            0.0,
            365,  # wagegwt  # daysinperiod
        )

        results = {}
        for name, func in output_metric_funcs.items():
            if name == "Total WFF Entitlement":
                results[name] = func(wff_df)
            elif name == "Total Tax Revenue":
                results[name] = func(tax_df)
            elif name == "Net Cost to Government":
                results[name] = func(tax_df, wff_df)
        return results

    baseline_results = _run_simulation(baseline_params)
    tasks = []
    for param_path in params_to_vary:
        params_low = copy.deepcopy(baseline_params)
        params_high = copy.deepcopy(baseline_params)

        current_value = _get_nested(params_low, param_path)
        low_value = current_value * (1 - pct_change)
        high_value = current_value * (1 + pct_change)

        _set_nested(params_low, param_path, low_value)
        _set_nested(params_high, param_path, high_value)

        tasks.append(delayed(_run_simulation)(params_low))
        tasks.append(delayed(_run_simulation)(params_high))

    # Run simulations in parallel
    parallel_results = Parallel(n_jobs=n_jobs)(tasks)

    # Process results
    output_data = {name: [] for name in output_metric_funcs}

    for i, param_path in enumerate(params_to_vary):
        low_results = parallel_results[i * 2]
        high_results = parallel_results[i * 2 + 1]
        for name in output_metric_funcs:
            output_data[name].append(
                {
                    "parameter": param_path,
                    "low_value": low_results[name],
                    "high_value": high_results[name],
                    "baseline": baseline_results[name],
                    "impact": high_results[name] - low_results[name],
                }
            )

    return {name: pd.DataFrame(data) for name, data in output_data.items()}


def run_probabilistic_analysis(
    param_distributions: Dict[str, Dict[str, Any]],
    num_samples: int,
    population_df: pd.DataFrame,
    output_metric_funcs: Dict[str, Callable[[pd.DataFrame, pd.DataFrame], float]],
    wff_runner: Callable,
    tax_runner: Callable,
    n_jobs: int = -1,
) -> Dict[str, np.ndarray]:
    """
    Perform a probabilistic sensitivity analysis on the microsimulation model.

    This analysis involves sampling from probability distributions for each
    parameter to be varied, and running the simulation for each sample. This
    is useful for understanding the uncertainty in the model's output due to
    uncertainty in the input parameters.

    Args:
        param_distributions: A dictionary defining the probability
            distribution for each parameter to be varied.
        num_samples: The number of samples to generate from the distributions.
        population_df: The population data to run the simulation on.
        output_metric_funcs: A dictionary of functions that each take a tax
            result and a WFF result DataFrame and return a single output
            metric.
        wff_runner: The function that runs the Working for Families simulation.
        tax_runner: The function that runs the tax simulation.
        n_jobs: The number of jobs to run in parallel. Defaults to -1, which
            uses all available CPU cores.

    Returns:
        A dictionary where keys are metric names and values are arrays
        containing the results from all the simulations for that metric.
    """
    from scipy.stats import norm, qmc, uniform

    sampler = qmc.LatinHypercube(d=len(param_distributions))
    sample = sampler.random(n=num_samples)

    def _run_simulation(sample_row):
        """Helper function to run a single simulation."""
        params = load_parameters("2023-2024").model_dump()

        for j, (param_path, dist_info) in enumerate(param_distributions.items()):
            if dist_info["dist"] == "norm":
                value = norm.ppf(sample_row[j], loc=dist_info["loc"], scale=dist_info["scale"])
            elif dist_info["dist"] == "uniform":
                value = uniform.ppf(sample_row[j], loc=dist_info["loc"], scale=dist_info["scale"])
            else:
                raise ValueError(f"Unsupported distribution: {dist_info['dist']}")
            _set_nested(params, param_path, value)

        tax_df = pd.DataFrame(
            {
                "tax": population_df["familyinc"].apply(
                    tax_runner,
                    args=(params["tax_brackets"]["rates"], params["tax_brackets"]["thresholds"]),
                )
            }
        )
        wff_df = wff_runner(population_df.copy(), params["wff"], 0.0, 365)

        results = {}
        for name, func in output_metric_funcs.items():
            if name == "Total WFF Entitlement":
                results[name] = func(wff_df)
            elif name == "Total Tax Revenue":
                results[name] = func(tax_df)
            elif name == "Net Cost to Government":
                results[name] = func(tax_df, wff_df)
        return results

    parallel_results = Parallel(n_jobs=n_jobs)(delayed(_run_simulation)(sample_row) for sample_row in sample)

    # Process results
    output_arrays = {name: [] for name in output_metric_funcs}
    for res in parallel_results:
        for name, value in res.items():
            output_arrays[name].append(value)

    return {name: np.array(data) for name, data in output_arrays.items()}


__all__ = ["run_deterministic_analysis", "run_probabilistic_analysis"]
