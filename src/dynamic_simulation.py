"""Dynamic simulation framework for the NZ microsimulation model.

This module provides a structure for running the microsimulation
consecutively across multiple policy years. It includes hooks for
demographic changes and behavioural responses.
"""

from __future__ import annotations

from typing import Callable, Dict, Sequence, Optional
import pandas as pd

from .microsim import load_parameters
from .parameters import Parameters
from .tax_calculator import TaxCalculator
from .behavioural import labour_supply_response as default_labour_supply_response
from .wff_microsim import famsim

BehaviouralFunc = Callable[[pd.DataFrame, pd.DataFrame, TaxCalculator, TaxCalculator, dict], pd.DataFrame]

def _run_static_simulation(df: pd.DataFrame, params: Parameters) -> pd.DataFrame:
    """Runs a single year's static simulation."""
    # This function now includes both tax and WFF calculations.

    current = df.copy()
    tax_calc = TaxCalculator(params=params)

    # Apply income tax
    current["tax_liability"] = current["taxable_income"].apply(tax_calc.income_tax)

    # Apply WFF calculations
    # We assume wagegwt=0 and daysinperiod=365 for this context.
    if params.wff:
        current = famsim(current, params.wff, wagegwt=0, daysinperiod=365)

    return current


def run_dynamic_simulation(
    df: pd.DataFrame,
    years: Sequence[str],
    use_behavioural_response: bool = False,
    elasticity_params: Optional[Dict] = None,
    behavioural_func: BehaviouralFunc = default_labour_supply_response,
) -> Dict[str, pd.DataFrame]:
    """
    Run a dynamic simulation by iterating the static model over several years.

    This function simulates the effects of policy changes over time. It can
    optionally include a labour supply response to policy changes.

    Args:
        df: The initial micro-data.
        years: A sequence of policy years to simulate.
        use_behavioural_response: If True, simulates labour supply response
            to policy changes between years.
        elasticity_params: A dictionary of elasticity parameters required
            if `use_behavioural_response` is True.
        behavioural_func: The function to use for the behavioural response.
            Defaults to `labour_supply_response`.

    Returns:
        A dictionary where keys are the simulated years and the values are
        the corresponding DataFrames with the simulation results.
    """
    results: Dict[str, pd.DataFrame] = {}
    df_current = df.copy()

    # Load the parameters for the year *before* the simulation starts
    # to have a baseline for the first year's behavioural response.
    try:
        first_year = int(years[0].split('-')[0])
        params_previous = load_parameters(f"{first_year - 1}-{first_year}")
        calc_previous = TaxCalculator(params=params_previous)
    except (ValueError, FileNotFoundError):
        print(f"Warning: Could not load parameters for year before {years[0]}. "
              "No behavioural response will be calculated for the first year.")
        calc_previous = None

    df_previous_year_end = df_current

    for year in years:
        params_current = load_parameters(year)
        calc_current = TaxCalculator(params=params_current)

        # Run the simulation for the current year's policies on last year's population
        df_after_policy = _run_static_simulation(df_previous_year_end, params_current)

        df_final_for_year = df_after_policy

        # If behavioural response is enabled, calculate it and update the dataframe
        if use_behavioural_response and calc_previous is not None:
            if elasticity_params is None:
                raise ValueError("elasticity_params must be provided if use_behavioural_response is True.")

            df_with_behavioural_change = behavioural_func(
                df_before=df_previous_year_end,
                df_after=df_after_policy,
                emtr_calculator_before=calc_previous,
                emtr_calculator_after=calc_current,
                elasticity_params=elasticity_params
            )

            # Re-run the simulation on the behaviourally adjusted data
            df_final_for_year = _run_static_simulation(df_with_behavioural_change, params_current)

        results[year] = df_final_for_year.copy()

        # The population at the end of this year becomes the starting point for the next
        df_previous_year_end = df_final_for_year
        calc_previous = calc_current

    return results


__all__ = ["run_dynamic_simulation"]
