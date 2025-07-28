"""Value of Information utilities."""

from typing import Dict

import numpy as np


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


__all__ = ["calculate_evpi"]
