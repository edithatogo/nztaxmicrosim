import json
import os
from typing import Any

from .parameters import FamilyBoostParams, IETCParams, Parameters, TaxBracketParams


def load_parameters(year: str) -> Parameters:
    """Load policy parameters for ``year``.

    Parameters are stored in JSON files named ``parameters_YYYY-YYYY.json``.
    This function parses the JSON into structured dataclasses, validating that
    all required fields are present and of the expected type.

    Args:
        year: The year for which to load the parameters (e.g., ``"2023-2024"``).

    Returns:
        Parameters: A dataclass containing all parameter groups for the year.
    """

    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, f"parameters_{year}.json")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Parameter file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        params: dict[str, Any] = json.load(f)

    try:
        return Parameters.from_dict(params)
    except (KeyError, TypeError) as e:
        raise ValueError(f"Parameter validation failed: {e}") from e


def taxit(taxy: float, params: TaxBracketParams) -> float:
    """Calculate income tax using progressive brackets.

    Args:
        taxy: The taxable income.
        params: Tax bracket parameters containing ``rates`` and ``thresholds``.

    Returns:
        The calculated income tax.
    """

    if taxy <= 0:
        return 0.0

    t_extended: list[float] = [0.0] + params.thresholds
    tax: float = 0.0

    for i, rate in enumerate(params.rates):
        if taxy > t_extended[i]:
            if i == len(t_extended) - 1 or taxy <= t_extended[i + 1]:
                tax += (taxy - t_extended[i]) * rate
                break
            tax += (t_extended[i + 1] - t_extended[i]) * rate
        else:
            break

    return tax


def calctax(taxy: float, split: int, params1: TaxBracketParams, params2: TaxBracketParams) -> float:
    """Calculate income tax for a split year."""

    taxa: float = taxit(taxy, params1)
    taxb: float = taxit(taxy, params2)
    return taxa * (split / 12) + taxb * ((12 - split) / 12)


def netavg(incvar: float, eprt: float, params: TaxBracketParams) -> float:
    """Calculate the net average income."""

    annearn: float = incvar * 52
    temptax: float = taxit(annearn, params)
    outnet: float = int(100 * (annearn * (1 - eprt) - temptax) / 52) / 100
    return outnet


def calcietc(
    taxable_income: float,
    is_wff_recipient: bool,
    is_super_recipient: bool,
    is_benefit_recipient: bool,
    ietc_params: IETCParams,
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

    income_threshold_min = ietc_params.thrin
    income_threshold_max = ietc_params.thrab
    max_entitlement = ietc_params.ent
    abatement_rate = ietc_params.abrate

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

    This function replicates the logic of the SAS macro `%eitc`.

    Args:
        is_credit_enabled (bool): A flag to indicate if the credit is on or off.
        is_eligible (bool): A flag to indicate if the person is eligible.
        income (float): The income variable.
        min_income_threshold (float): The income threshold to be eligible.
        max_entitlement_income (float): The income point at which the maximum entitlement is first attained.
        abatement_income_threshold (float): The income point at which the entitlement starts to abate.
        earning_rate (float): The rate at which the credit is earned.
        abatement_rate (float): The rate at which the credit is abated.

    Returns:
        float: The calculated EITC.
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


def simrwt(
    interest: float,
    rwt_rate_10_5: float,
    rwt_rate_17_5: float,
    rwt_rate_30: float,
    rwt_rate_33: float,
    rwt_rate_39: float,
) -> float:
    """
    Simulates the Resident Withholding Tax (RWT).

    This function replicates the logic of the SAS macro `%simrwt`.

    Args:
        interest (float): The interest income.
        rwt_rate_10_5 (float): The RWT rate for the 10.5% tax bracket.
        rwt_rate_17_5 (float): The RWT rate for the 17.5% tax bracket.
        rwt_rate_30 (float): The RWT rate for the 30% tax bracket.
        rwt_rate_33 (float): The RWT rate for the 33% tax bracket.
        rwt_rate_39 (float): The RWT rate for the 39% tax bracket.

    Returns:
        float: The calculated RWT.
    """
    if interest <= 0:
        return 0.0
    else:
        outtax: float = interest * (
            0.0
            + 1.05 * rwt_rate_10_5
            + 1.75 * rwt_rate_17_5
            + 0.30 * rwt_rate_30
            + 0.33 * rwt_rate_33
            + 0.39 * rwt_rate_39
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
    Calculates standard superannuation.

    This function replicates the logic of the SAS macro `%supstd`.

    Args:
        cpi_factors (list[float]): A list of 4 CPI factors for the simulation years.
        average_weekly_earnings (list[float]): A list of 4 average weekly earnings for the simulation years.
        earner_premium_rates (list[float]): A list of 4 earner premium rates for the simulation years.
        super_floor_relativities (list[float]): A list of 4 superannuation accord
            floor relativities for the simulation years.
        tax_parameters (list[TaxBracketParams]): A list of 4 parameter sets for
            the simulation years.
        base_year_average_weekly_earnings (float): The average weekly earnings for the base year.
        base_year_earner_premium_rate (float): The earner premium rate for the base year.
        base_year_tax_parameters (TaxBracketParams): Tax parameters for the base year.

    Returns:
        dict: A dictionary containing the calculated standard superannuation amounts.
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

    Args:
        family_income: The total family income.
        childcare_costs: The total childcare costs.
        family_boost_params: FamilyBoost parameter dataclass.

    Returns:
        float: The calculated FamilyBoost credit.
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
