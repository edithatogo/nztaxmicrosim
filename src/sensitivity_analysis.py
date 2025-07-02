from typing import Any, Callable, Dict, List

import pandas as pd
from joblib import Parallel, delayed


def run_deterministic_analysis(
    baseline_params: Dict[str, Any],
    params_to_vary: List[str],
    pct_change: float,
    population_df: pd.DataFrame,
    output_metric_func: Callable[[pd.DataFrame], float],
    wff_runner: Callable,
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

    Returns:
        pd.DataFrame: A DataFrame with the results of the sensitivity analysis.
    """

    def _run_simulation(params):
        """Helper function to run a single simulation."""
        # Note: This assumes wff_runner expects params['wff'], wagegwt, and daysinperiod
        # This might need to be made more flexible in the future.
        result_df = wff_runner(
            population_df.copy(),
            params["wff"],
            0.0,  # wagegwt
            365,  # daysinperiod
        )
        return output_metric_func(result_df)

    tasks = []
    for param_path in params_to_vary:
        # Create copies of the baseline parameters
        params_low = pd.json_normalize(baseline_params).to_dict(orient="records")[0]
        params_high = pd.json_normalize(baseline_params).to_dict(orient="records")[0]

        # Get the current value
        current_value = params_low[param_path]

        # Calculate the new values
        low_value = current_value * (1 - pct_change)
        high_value = current_value * (1 + pct_change)

        # Update the parameters
        params_low[param_path] = low_value
        params_high[param_path] = high_value

        # Un-flatten the parameters
        params_low = pd.json_normalize(params_low).iloc[0].to_dict()
        params_high = pd.json_normalize(params_high).iloc[0].to_dict()

        tasks.append(delayed(_run_simulation)(params_low))
        tasks.append(delayed(_run_simulation)(params_high))

    # Run simulations in parallel
    results = Parallel(n_jobs=-1)(tasks)

    # Process results
    output_data = []
    for i, param_path in enumerate(params_to_vary):
        baseline_result = output_metric_func(wff_runner(population_df.copy(), baseline_params["wff"], 0.0, 365))
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
