from dataclasses import asdict
from typing import Any, Callable, Dict, List

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

from src.microsim import load_parameters


def _get_nested(d: Dict[str, Any], path: str) -> Any:
    """
    Gets a value from a nested dictionary or list using a dot-separated path.

    Args:
        d (Dict[str, Any]): The dictionary or list to traverse.
        path (str): The dot-separated path to the desired value (e.g., "key1.nested_key.0.final_key").

    Returns:
        Any: The value found at the specified path.
    """
    keys = path.split(".")
    for key in keys:
        if isinstance(d, list):
            d = d[int(key)]
        else:
            d = d[key]
    return d


def _set_nested(d: Dict[str, Any], path: str, value: Any) -> None:
    """
    Sets a value in a nested dictionary or list using a dot-separated path.

    Args:
        d (Dict[str, Any]): The dictionary or list to modify.
        path (str): The dot-separated path to the location where the value should be set.
        value (Any): The value to set at the specified path.
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
) -> Dict[str, pd.DataFrame]:
    """
    Performs a deterministic sensitivity analysis on the microsimulation model for multiple output metrics.

    Args:
        baseline_params (Dict[str, Any]): The baseline set of parameters.
        params_to_vary (List[str]): A list of parameter names to vary.
        pct_change (float): The percentage change to apply to each parameter.
        population_df (pd.DataFrame): The population data to run the simulation on.
        output_metric_funcs (Dict[str, Callable]): A dictionary of functions that each take a
            tax result and a wff result DataFrame and return a single output metric.
        wff_runner (Callable): The function that runs the WFF simulation.
        tax_runner (Callable): The function that runs the tax simulation.

    Returns:
        Dict[str, pd.DataFrame]: A dictionary where keys are metric names and values are
            DataFrames with the sensitivity analysis results for that metric.
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

    tasks = []
    for param_path in params_to_vary:
        params_low = pd.DataFrame([baseline_params]).to_dict(orient="records")[0]
        params_high = pd.DataFrame([baseline_params]).to_dict(orient="records")[0]

        current_value = _get_nested(params_low, param_path)
        low_value = current_value * (1 - pct_change)
        high_value = current_value * (1 + pct_change)

        _set_nested(params_low, param_path, low_value)
        _set_nested(params_high, param_path, high_value)

        tasks.append(delayed(_run_simulation)(params_low))
        tasks.append(delayed(_run_simulation)(params_high))

    # Run simulations in parallel
    parallel_results = Parallel(n_jobs=-1)(tasks)

    # Process results
    baseline_results = _run_simulation(baseline_params)
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
) -> Dict[str, np.ndarray]:
    """
    Performs a probabilistic sensitivity analysis on the microsimulation model.

    Args:
        param_distributions (Dict[str, Dict[str, Any]]): A dictionary defining the
            probability distribution for each parameter to be varied.
        num_samples (int): The number of samples to generate.
        population_df (pd.DataFrame): The population data to run the simulation on.
        output_metric_funcs (Dict[str, Callable]): A dictionary of functions that each take a
            tax result and a wff result DataFrame and return a single output metric.
        wff_runner (Callable): The function that runs the WFF simulation.
        tax_runner (Callable): The function that runs the tax simulation.

    Returns:
        Dict[str, np.ndarray]: A dictionary where keys are metric names and values are
            arrays with the results from all the simulations for that metric.
    """
    from scipy.stats import norm, qmc, uniform

    sampler = qmc.LatinHypercube(d=len(param_distributions))
    sample = sampler.random(n=num_samples)

    def _run_simulation(sample_row):
        """Helper function to run a single simulation."""
        params = asdict(load_parameters("2023-2024"))

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

    parallel_results = Parallel(n_jobs=-1)(delayed(_run_simulation)(sample_row) for sample_row in sample)

    # Process results
    output_arrays = {name: [] for name in output_metric_funcs}
    for res in parallel_results:
        for name, value in res.items():
            output_arrays[name].append(value)

    return {name: np.array(data) for name, data in output_arrays.items()}


__all__ = ["run_deterministic_analysis", "run_probabilistic_analysis"]
