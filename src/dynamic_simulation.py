"""Simple dynamic simulation framework for the NZ microsimulation model.

This module provides a minimal structure for running the microsimulation
consecutively across multiple policy years. It introduces a hook for
labor supply responses but intentionally keeps the logic lightweight.

The project roadmap highlights the future goal of extending the model to
"dynamic simulation" with demographic and economic changes over time.
See ``README.md`` lines 188-194 for the broader context.
"""

from __future__ import annotations

from typing import Callable, Dict, Sequence

import pandas as pd

from .microsim import load_parameters, taxit
from .parameters import Parameters

LabourFunc = Callable[[pd.DataFrame, Parameters], pd.DataFrame]


def run_dynamic_simulation(
    df: pd.DataFrame,
    years: Sequence[str],
    labour_response: LabourFunc | None = None,
) -> Dict[str, pd.DataFrame]:
    """
    Run a dynamic simulation by iterating the static model over several years.

    This function simulates the effects of policy changes over time by running
    the microsimulation model sequentially for each year in the `years`
    sequence. The output of one year's simulation can be used as the input
    for the next, and an optional `labour_response` function can be used to
    model changes in labour supply between years.

    Args:
        df: The initial micro-data, containing at least a `taxable_income`
            column.
        years: A sequence of policy years (e.g., `["2023-2024", "2024-2025"]`)
            to simulate.
        labour_response: An optional function that adjusts the DataFrame for
            labour supply effects. It is called for each year in the
            simulation, and receives the DataFrame from the previous year and
            the parameters for the current year. It must return an updated
            DataFrame.

    Returns:
        A dictionary where the keys are the simulated years and the values are
        the corresponding DataFrames with the simulation results.
    """
    results: Dict[str, pd.DataFrame] = {}
    current = df.copy()

    for year in years:
        params = load_parameters(year)

        if labour_response is not None:
            current = labour_response(current, params)

        current = current.copy()
        current["tax_liability"] = current["taxable_income"].apply(lambda inc: taxit(inc, params.tax_brackets))

        # Assuming daysinperiod is constant for simplicity.
        # A more robust implementation might get this from parameters.
        daysinperiod = 365

        # Assuming wagegwt is 0 for simplicity.
        wagegwt = 0

        # Import famsim here to avoid circular dependency at module level.
        from .wff_microsim import famsim

        current = famsim(current, params.wff, wagegwt, daysinperiod)

        results[year] = current.copy()

    return results


__all__ = ["run_dynamic_simulation"]
