from __future__ import annotations

import json
import os
from typing import Any, Mapping

from pydantic import ValidationError

from .parameters import (
    Parameters,
    TaxBracketParams,
)


import sqlite3

# Define the path to the database as a module-level constant to allow patching in tests
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "parameters.db")

def load_parameters(year: str) -> Parameters:
    """Load policy parameters for ``year`` from the SQLite database.

    This function connects to the parameters database, queries for all policy
    parameters for the given year, reconstructs the parameter dictionary,
    and validates it using the Pydantic model.

    Args:
        year: The start year for which to load the parameters (e.g., ``"2023"``).
              Note: The input should be the start year as an integer or string,
              not the "YYYY-YYYY" format.

    Returns:
        Parameters: A Pydantic model containing all parameter groups for the year.
    """
    # The database stores years as integers (e.g., 2023 for "2023-2024")
    try:
        start_year = int(year.split('-')[0])
    except (ValueError, IndexError):
        start_year = int(year)

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Parameters database not found at {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT policy_key, parameters FROM policy_parameters WHERE year = ?", (start_year,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        raise ValueError(f"No parameters found for year {start_year} in the database.")

    params_dict = {}
    for key, params_json in rows:
        if params_json is not None:
            params_dict[key] = json.loads(params_json)
        else:
            params_dict[key] = None

    try:
        return Parameters.model_validate(params_dict)
    except ValidationError as e:
        raise ValueError(f"Parameter validation for year {start_year} failed: {e}") from e


def _coerce_tax_brackets(params: Mapping[str, Any] | TaxBracketParams) -> TaxBracketParams:
    """Convert a mapping of tax parameters into :class:`TaxBracketParams`."""

    if isinstance(params, TaxBracketParams):
        return params
    return TaxBracketParams.model_validate(
        {
            "rates": params["rates"],
            "thresholds": params["thresholds"],
        }
    )


def taxit(taxy: float, params: Mapping[str, Any] | TaxBracketParams) -> float:
    """
    Calculate income tax using a progressive tax bracket system.

    This function iterates through the tax brackets defined in `params`. For each
    bracket, it calculates the tax owed on the portion of income that falls
    within that bracket's range. The total tax is the sum of the tax from
    each bracket.

    Args:
        taxy: The taxable income.
        params: A `TaxBracketParams` instance or a mapping containing
            `rates` and `thresholds` for the tax brackets.

    Returns:
        The total calculated income tax.
    """

    if taxy <= 0:
        return 0.0

    tax_params = _coerce_tax_brackets(params)
    t_extended: list[float] = [0.0] + tax_params.thresholds
    tax: float = 0.0

    for i, rate in enumerate(tax_params.rates):
        if taxy > t_extended[i]:
            if i == len(t_extended) - 1 or taxy <= t_extended[i + 1]:
                tax += (taxy - t_extended[i]) * rate
                break
            tax += (t_extended[i + 1] - t_extended[i]) * rate
        else:
            break

    return tax


def calctax(taxy: float, split: int, params1: TaxBracketParams, params2: TaxBracketParams) -> float:
    """
    Calculate income tax for a year with a mid-year policy change (split year).

    This is used when tax rules change during a financial year. It calculates
    the tax for the full year under the old rules (`params1`) and the new rules
    (`params2`), then prorates the results based on the `split` month.

    Args:
        taxy: The total taxable income for the year.
        split: The month number (1-12) in which the tax change occurs. The
            new rules apply from this month onwards.
        params1: The tax bracket parameters for the first part of the year.
        params2: The tax bracket parameters for the second part of the year.

    Returns:
        The total income tax for the split year.
    """

    taxa: float = taxit(taxy, params1)
    taxb: float = taxit(taxy, params2)
    return taxa * (split / 12) + taxb * ((12 - split) / 12)


def calculate_net_weekly_income(
    gross_weekly_income: float,
    acc_earners_premium_rate: float,
    tax_params: TaxBracketParams,
) -> float:
    """
    Calculate the net average weekly income after tax and ACC levy.

    This function annualizes the weekly income, calculates the annual income tax,
    deducts the ACC Earner's Premium, and then converts the result back to a
    weekly net income.

    Args:
        gross_weekly_income: The gross weekly income.
        acc_earners_premium_rate: The ACC Earner's Premium rate.
        tax_params: The tax bracket parameters.

    Returns:
        The net average weekly income, rounded to two decimal places.
    """
    annual_earnings = gross_weekly_income * 52
    annual_tax = taxit(annual_earnings, tax_params)
    net_annual_income = annual_earnings * (1 - acc_earners_premium_rate) - annual_tax
    net_weekly_income = int(100 * net_annual_income / 52) / 100
    return net_weekly_income


def simrwt(interest: float, rwt_rate: float) -> float:
    """
    Calculates the Resident Withholding Tax (RWT).

    Args:
        interest (float): The interest income.
        rwt_rate (float): The RWT rate to apply.

    Returns:
        float: The calculated RWT.
    """
    if interest <= 0:
        return 0.0
    if not (0 <= rwt_rate <= 1):
        raise ValueError("RWT rate must be between 0 and 1.")
    return interest * rwt_rate


def supstd(
    cpi_factors: list[float],
    average_weekly_earnings: list[float],
    earner_premium_rates: list[float],
    super_floor_relativities: list[float],
    tax_parameters: list[TaxBracketParams],
    base_year_average_weekly_earnings: float,
    base_year_earner_premium_rate: float,
    base_year_tax_parameters: TaxBracketParams,
) -> dict[str, float]:
    """
    Calculates standard superannuation rates for a base year and 4 simulation years.

    This function projects superannuation payments, ensuring they are indexed
    to the higher of CPI inflation or a "floor" relative to the average weekly
    earnings. It calculates both gross and net superannuation amounts.

    This function replicates the logic of the SAS macro `%supstd`.

    Args:
        cpi_factors: A list of 4 CPI factors for the simulation years.
        average_weekly_earnings: A list of 4 average weekly earnings for the
            simulation years.
        earner_premium_rates: A list of 4 ACC earner premium rates for the
            simulation years.
        super_floor_relativities: A list of 4 superannuation accord floor
            relativities for the simulation years.
        tax_parameters: A list of 4 tax parameter sets for the simulation years.
        base_year_average_weekly_earnings: The average weekly earnings for the
            base year.
        base_year_earner_premium_rate: The ACC earner premium rate for the
            base year.
        base_year_tax_parameters: Tax parameters for the base year.

    Returns:
        A dictionary containing the calculated gross and net standard
        superannuation amounts for the base year and 4 simulation years.
    """
    results: dict[str, float] = {}

    # Base year
    base_year_super: float = base_year_average_weekly_earnings * 0.66 * 2
    base_year_net_super: float = calculate_net_weekly_income(
        gross_weekly_income=base_year_super / 2,
        acc_earners_premium_rate=base_year_earner_premium_rate,
        tax_params=base_year_tax_parameters,
    )
    results["std22"] = base_year_super
    results["stdnet22"] = base_year_net_super

    # Simulation years
    super_values: list[float] = []
    net_super_values: list[float] = []

    previous_super: float = base_year_super
    for i in range(4):
        current_super: float = max(
            average_weekly_earnings[i] * super_floor_relativities[i] * 2,
            previous_super * cpi_factors[i],
        )
        net_super: float = calculate_net_weekly_income(
            gross_weekly_income=current_super / 2,
            acc_earners_premium_rate=earner_premium_rates[i],
            tax_params=tax_parameters[i],
        )
        super_values.append(current_super)
        net_super_values.append(net_super)
        previous_super = current_super

    results["std"] = super_values[0]
    results["stdnet"] = net_super_values[0]
    results["std1"] = super_values[1]
    results["stdnet1"] = net_super_values[1]
    results["std2"] = super_values[2]
    results["stdnet2"] = net_super_values[2]
    results["std3"] = super_values[3]
    results["stdnet3"] = net_super_values[3]

    return results
