"""Value of Information utilities."""

from typing import Dict, List

import numpy as np
import pandas as pd


def calculate_evppi(
    psa_results: Dict[str, np.ndarray],
    psa_parameters: Dict[str, np.ndarray],
    param_names: List[str],
    n_bins: int = 10,
) -> Dict[str, float]:
    """Calculate the Expected Value of Perfect Partial Information (EVPPI).

    Parameters
    ----------
    psa_results : Dict[str, np.ndarray]
        Dictionary mapping output metric names to two-dimensional arrays of
        probabilistic sensitivity analysis results. Each array must have shape
        ``(n_options, n_simulations)`` where ``n_options`` is the number of
        decision options being compared and ``n_simulations`` is the number of
        PSA iterations.
    psa_parameters : Dict[str, np.ndarray]
        Dictionary mapping parameter names to one-dimensional arrays of
        parameter values from the PSA. Each array must have shape
        ``(n_simulations,)``.
    param_names : List[str]
        A list of parameter names for which to calculate the EVPPI.
    n_bins : int, optional
        The number of bins to use when discretizing continuous parameters, by default 10.

    Returns
    -------
    Dict[str, float]
        A dictionary mapping each metric name to its EVPPI value for the
        specified set of parameters.

    Notes
    -----
    EVPPI represents the expected gain in the chosen outcome metric if the true
    value of a specific subset of parameters were known with certainty before
    making a decision. It is estimated using a non-parametric regression
    approach.

    The calculation proceeds as follows:
    1. For each parameter in `param_names`, its sample from the PSA is
       discretized into `n_bins` bins if continuous.
    2. The PSA simulations are grouped based on the combination of parameter bins/values.
    3. For each group, we compute the expected outcome for each decision option.
    4. We identify the best decision option for each group.
    5. The expected outcome with partial perfect information is the average of
       the outcomes of the best option in each group, weighted by group size.
    6. The EVPPI is the difference between this value and the expected outcome
       with current information.
    """
    if not param_names:
        return {metric: 0.0 for metric in psa_results}

    for param in param_names:
        if param not in psa_parameters:
            raise ValueError(f"Parameter '{param}' not found in psa_parameters.")

    n_simulations = psa_parameters[param_names[0]].shape[0]

    df = pd.DataFrame()
    for param in param_names:
        p_data = psa_parameters[param]
        if p_data.shape != (n_simulations,):
            raise ValueError(f"Parameter '{param}' has incorrect shape {p_data.shape}, expected ({n_simulations},)")
        if np.issubdtype(p_data.dtype, np.number) and len(np.unique(p_data)) > n_bins:
            df[param] = pd.cut(p_data, bins=n_bins, labels=False)
        else:
            df[param] = p_data

    evppi_values: Dict[str, float] = {}
    for metric, data in psa_results.items():
        if data.ndim != 2 or data.shape[1] != n_simulations:
            raise ValueError(
                f"Values in psa_results must be 2D arrays of shape (n_options, {n_simulations}); "
                f"got {data.shape} for metric '{metric}'"
            )

        mean_current = float(np.max(np.mean(data, axis=1)))

        metric_df = df.copy()
        for i in range(data.shape[0]):
            metric_df[f"option_{i}"] = data[i, :]

        grouped = metric_df.groupby(param_names)
        mean_outcomes_in_bins = grouped[[f"option_{i}" for i in range(data.shape[0])]].mean()
        max_mean_outcomes = mean_outcomes_in_bins.max(axis=1)
        bin_counts = grouped.size()
        weighted_max_outcomes = max_mean_outcomes * bin_counts
        expected_value_partial_info = weighted_max_outcomes.sum() / n_simulations

        evppi_values[metric] = expected_value_partial_info - mean_current

    return evppi_values


def calculate_evpi(psa_results: Dict[str, np.ndarray]) -> Dict[str, float]:
    """Calculate the Expected Value of Perfect Information (EVPI).

    Parameters
    ----------
    psa_results : Dict[str, np.ndarray]
        Dictionary mapping output metric names to two-dimensional arrays of
        probabilistic sensitivity analysis results. Each array must have shape
        ``(n_options, n_simulations)`` where ``n_options`` is the number of
        decision options being compared and ``n_simulations`` is the number of
        PSA iterations.

    Returns
    -------
    Dict[str, float]
        A dictionary mapping each metric name to its EVPI value.

    Notes
    -----
    EVPI represents the expected gain in the chosen outcome metric if the true
    state of the world (i.e., the uncertain parameters) were known with
    certainty before making a decision. For each metric, EVPI is computed as::

        EVPI = E[max_j x_{ij}] - max_i E[x_{ij}]

    where ``x_{ij}`` is the simulated outcome for option ``i`` in simulation
    ``j``.
    """

    evpi_values: Dict[str, float] = {}
    for metric, data in psa_results.items():
        if data.ndim != 2:
            raise ValueError(
                f"Values in psa_results must be 2D arrays of shape (n_options, n_simulations); got {data.ndim}D array"
            )

        # Expected value with perfect information: pick the best option for each simulation
        mean_perfect = float(np.mean(np.max(data, axis=0)))

        # Expected value with current information: pick the option with the highest mean outcome
        mean_current = float(np.max(np.mean(data, axis=1)))

        evpi_values[metric] = mean_perfect - mean_current

    return evpi_values


__all__ = ["calculate_evpi", "calculate_evppi"]
