"""Provides a unified interface for running static and dynamic simulations."""

from typing import Dict, List, Union

import pandas as pd

from .dynamic_simulation import run_dynamic_simulation


def run_simulation(
    df: pd.DataFrame,
    mode: str,
    year: Union[str, List[str]],
    labour_response=None,
) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """
    Run a microsimulation in either static or dynamic mode.

    This function provides a unified interface for running both static and
    dynamic simulations. In static mode, the simulation is run for a single
    year. In dynamic mode, the simulation is run for a series of years, with
    the output of one year being used as the input for the next.

    Args:
        df: The input population data.
        mode: The simulation mode, either 'static' or 'dynamic'.
        year: A single year (e.g., "2023-2024") for static mode, or a list
            of years for dynamic mode.
        labour_response: An optional function to model labour supply
            changes in dynamic mode.

    Returns:
        For static mode, a DataFrame containing the simulation results for the
        specified year. For dynamic mode, a dictionary of DataFrames, where
        each key is a year and the value is the simulation results for that
        year.
    """
    if mode == "static":
        if not isinstance(year, str):
            raise ValueError("A single year must be provided for static mode.")

        results = run_dynamic_simulation(df, [year], labour_response)
        return results[year]

    elif mode == "dynamic":
        if not isinstance(year, list):
            raise ValueError("A list of years must be provided for dynamic mode.")

        return run_dynamic_simulation(df, year, labour_response)

    else:
        raise ValueError(f"Invalid mode: {mode}. Must be 'static' or 'dynamic'.")


__all__ = ["run_simulation"]
