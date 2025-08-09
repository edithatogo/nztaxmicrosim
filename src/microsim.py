from __future__ import annotations

import json
import os
from typing import Any, Mapping

from pydantic import ValidationError

from .historical_data import get_historical_parameters
from .parameters import (
    FamilyBoostParams,
    IETCParams,
    Parameters,
    RWTParams,
    TaxBracketParams,
)


def load_parameters(year: str) -> Parameters:
    """Load policy parameters for ``year``.

    Parameters are stored in JSON files named ``parameters_YYYY-YYYY.json``.
    This function parses the JSON into Pydantic models, validating that all
    required fields are present and of the expected type.

    If a specific parameter file for the given year is not found, it falls
    back to the historical data.

    Args:
        year: The year for which to load the parameters (e.g., ``"2023-2024"``).

    Returns:
        Parameters: A Pydantic model containing all parameter groups for the year.
    """

    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, f"parameters_{year}.json")

    if not os.path.exists(file_path):
        try:
            return get_historical_parameters(year)
        except FileNotFoundError:
            raise FileNotFoundError(f"Parameter file not found for year {year}, and no historical data available.")

    with open(file_path, "r", encoding="utf-8") as f:
        params: dict[str, Any] = json.load(f)

    try:
        return Parameters.model_validate(params)
    except ValidationError as e:
        raise ValueError(f"Parameter validation failed: {e}") from e



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


def netavg(incvar: float, eprt: float, params: TaxBracketParams) -> float:
    """
    Calculate the net average weekly income after tax and ACC levy.

    This function annualizes the weekly income, calculates the annual income tax,
    deducts the ACC Earner's Premium, and then converts the result back to a
    weekly net income.

    Args:
        incvar: The gross weekly income.
        eprt: The ACC Earner's Premium rate.
        params: The tax bracket parameters.

    Returns:
        The net average weekly income, rounded to two decimal places.
    """

    annearn: float = incvar * 52
    temptax: float = taxit(annearn, params)
    outnet: float = int(100 * (annearn * (1 - eprt) - temptax) / 52) / 100
    return outnet


def _coerce_ietc(params: Mapping[str, Any] | IETCParams) -> IETCParams:
    if isinstance(params, IETCParams):
        return params
    return IETCParams.model_validate(params)  # type: ignore[arg-type]


def calcietc(
    taxable_income: float,
    is_wff_recipient: bool,
    is_super_recipient: bool,
    is_benefit_recipient: bool,
    ietc_params: Mapping[str, Any] | IETCParams,
) -> float:
    """
    Calculates the Independent Earner Tax Credit (IETC).

    This function determines the IETC entitlement based on taxable income and
    eligibility criteria. It replicates the logic of the SAS macro `%calcietc`.

    Args:
        taxable_income (float): The individual's taxable income.
        is_wff_recipient (bool): True if the individual receives Working for Families tax credits.
        is_super_recipient (bool): True if the individual receives superannuation payments.
        is_benefit_recipient (bool): True if the individual receives a main benefit.
        ietc_params: Structured IETC parameters.

    Returns:
        float: The calculated IETC amount.
    """
    # IETC is not available to recipients of WFF, superannuation, or main benefits.
    if is_wff_recipient or is_super_recipient or is_benefit_recipient:
        return 0.0

    params = _coerce_ietc(ietc_params)
    income_threshold_min = params.thrin
    income_threshold_max = params.thrab
    max_entitlement = params.ent
    abatement_rate = params.abrate

    # Calculate IETC based on income thresholds.
    if taxable_income <= income_threshold_min:
        return 0.0
    elif taxable_income <= income_threshold_max:
        return max_entitlement
    else:
        # Abate the credit for income above the maximum threshold.
        abatement = (taxable_income - income_threshold_max) * abatement_rate
        return max(0.0, max_entitlement - abatement)


def eitc(
    is_credit_enabled: bool,
    is_eligible: bool,
    income: float,
    min_income_threshold: float,
    max_entitlement_income: float,
    abatement_income_threshold: float,
    earning_rate: float,
    abatement_rate: float,
) -> float:
    """
    Calculates the Earned Income Tax Credit (EITC).

    The EITC calculation has three phases based on income:
    1.  **Phase-in:** For income between `min_income_threshold` and
        `max_entitlement_income`, the credit increases at the `earning_rate`.
    2.  **Plateau:** For income between `max_entitlement_income` and
        `abatement_income_threshold`, the credit is at its maximum.
    3.  **Phase-out:** For income above `abatement_income_threshold`, the
        credit is reduced at the `abatement_rate`.

    This function replicates the logic of the SAS macro `%eitc`.

    Args:
        is_credit_enabled: Flag to enable or disable the credit calculation.
        is_eligible: Flag indicating if the individual is eligible for the credit.
        income: The income amount to base the calculation on.
        min_income_threshold: The income level at which the credit begins.
        max_entitlement_income: The income level where the credit reaches its maximum.
        abatement_income_threshold: The income level at which the credit begins to abate.
        earning_rate: The rate at which the credit is earned during phase-in.
        abatement_rate: The rate at which the credit is reduced during phase-out.

    Returns:
        The calculated EITC amount.
    """
    if not is_credit_enabled or not is_eligible:
        return 0.0

    if income <= min_income_threshold:
        return 0.0
    elif income <= max_entitlement_income:
        return earning_rate * (income - min_income_threshold)
    elif income <= abatement_income_threshold:
        return (max_entitlement_income - min_income_threshold) * earning_rate
    else:
        return max(
            0.0,
            (max_entitlement_income - min_income_threshold) * earning_rate
            - (income - abatement_income_threshold) * abatement_rate,
        )


def simrwt(interest: float, params: RWTParams) -> float:
    """
    Simulates the Resident Withholding Tax (RWT).

    This function replicates the logic of the SAS macro `%simrwt`.

    Args:
        interest (float): The interest income.
        params (RWTParams): The RWT parameters containing rates for each tax bracket.

    Returns:
        float: The calculated RWT.
    """
    if interest <= 0:
        return 0.0
    outtax: float = interest * (
        0.0
        + 1.05 * params.rwt_rate_10_5
        + 1.75 * params.rwt_rate_17_5
        + 0.30 * params.rwt_rate_30
        + 0.33 * params.rwt_rate_33
        + 0.39 * params.rwt_rate_39
    )
    return min(interest, outtax)


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
    base_year_net_super: float = netavg(
        base_year_super / 2,
        base_year_earner_premium_rate,
        base_year_tax_parameters,
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
        net_super: float = netavg(
            current_super / 2,
            earner_premium_rates[i],
            tax_parameters[i],
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


def family_boost_credit(
    family_income: float,
    childcare_costs: float,
    family_boost_params: FamilyBoostParams,
) -> float:
    """
    Calculates the FamilyBoost childcare tax credit.

    The credit is calculated as 25% of childcare costs, up to a maximum
    credit amount. The credit is then abated for families with income above
    a certain threshold.

    Args:
        family_income: The total family income.
        childcare_costs: The total childcare costs for the period.
        family_boost_params: The parameters for the FamilyBoost credit,
            including max credit, income thresholds, and abatement rate.

    Returns:
        The calculated FamilyBoost credit amount.
    """
    max_credit = family_boost_params.max_credit
    income_threshold = family_boost_params.income_threshold
    abatement_rate = family_boost_params.abatement_rate
    max_income = family_boost_params.max_income

    if family_income > max_income:
        return 0.0

    credit = min(childcare_costs * 0.25, max_credit)

    if family_income > income_threshold:
        abatement = (family_income - income_threshold) * abatement_rate
        credit = max(0.0, credit - abatement)

    return credit
