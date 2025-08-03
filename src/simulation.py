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
    Runs a microsimulation in either static or dynamic mode.

    Args:
        df (pd.DataFrame): The input population data.
        mode (str): The simulation mode, either 'static' or 'dynamic'.
        year (Union[str, List[str]]): A single year for static mode, or a list
            of years for dynamic mode.
        labour_response (function, optional): A function to model labour supply
            changes in dynamic mode. Defaults to None.

    Returns:
        Union[pd.DataFrame, Dict[str, pd.DataFrame]]: A DataFrame for static
            mode, or a dictionary of DataFrames for dynamic mode.
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
