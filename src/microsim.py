import json
import os
from typing import Any

from pydantic import ValidationError

from .parameters_model import TaxParameters


def load_parameters(year: str) -> dict[str, Any]:
    """
    Loads tax parameters from a JSON file for a specific year.

    Args:
        year (str): The year for which to load the parameters (e.g., "2023-2024").

    Returns:
        dict: A dictionary containing the tax parameters.
    """
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, f"parameters_{year}.json")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Parameter file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        params = json.load(f)

    try:
        validated = TaxParameters.model_validate(params)
    except ValidationError as e:
        raise ValueError(f"Parameter validation failed: {e}") from e

    return validated.model_dump()


def taxit(taxy: float, r: list[float], t: list[float]) -> float:
    """
    Calculates income tax based on a progressive tax system with multiple brackets.

    This function replicates the logic of the SAS macro `%taxit`.

    Args:
        taxy (float): The taxable income.
        r (list): A list of tax rates for each bracket.
        t (list): A list of tax thresholds for each bracket.

    Returns:
        float: The calculated income tax.
    """
    if taxy <= 0:
        return 0.0

    # Add a zero threshold to the beginning of the list for easier calculation
    t_extended: list[float] = [0.0] + t

    # Initialize tax to 0
    tax: float = 0.0

    # Iterate through the tax brackets
    for i in range(len(r)):
        # If the taxable income is within the current bracket
        if taxy > t_extended[i]:
            # If this is the last bracket or the taxable income is less than the next threshold
            if i == len(t_extended) - 1 or taxy <= t_extended[i + 1]:
                tax += (taxy - t_extended[i]) * r[i]
                break
            # If the taxable income is greater than the next threshold
            else:
                tax += (t_extended[i + 1] - t_extended[i]) * r[i]
        else:
            break

    return tax


def calctax(taxy: float, split: int, r1: list[float], t1: list[float], r2: list[float], t2: list[float]) -> float:
    """
    Calculates income tax for a split year.

    This function replicates the logic of the SAS macro `%calctax`.

    Args:
        taxy (float): The taxable income.
        split (int): The number of months in the first part of the year.
        r1 (list): A list of tax rates for the first part of the year.
        t1 (list): A list of tax thresholds for the first part of the year.
        r2 (list): A list of tax rates for the second part of the year.
        t2 (list): A list of tax thresholds for the second part of the year.

    Returns:
        float: The calculated income tax.
    """
    taxa: float = taxit(taxy, r1, t1)
    taxb: float = taxit(taxy, r2, t2)
    return taxa * (split / 12) + taxb * ((12 - split) / 12)


def netavg(incvar: float, eprt: float, pct: list[float], thr: list[float]) -> float:
    """
    Calculates the net average income.

    This function replicates the logic of the SAS macro `%netavg`.

    Args:
        incvar (float): The income variable.
        eprt (float): The earner premium rate.
        pct (list): A list of tax rates for each bracket.
        thr (list): A list of tax thresholds for each bracket.

    Returns:
        float: The net average income.
    """
    annearn: float = incvar * 52
    temptax: float = taxit(annearn, pct, thr)
    outnet: float = int(100 * (annearn * (1 - eprt) - temptax) / 52) / 100
    return outnet


def calcietc(
    taxable_income: float,
    is_wff_recipient: bool,
    is_super_recipient: bool,
    is_benefit_recipient: bool,
    ietc_params: dict[str, float],
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
        ietc_params (dict): A dictionary of IETC parameters, including:
            - "thrin" (float): The income threshold below which no IETC is earned.
            - "thrab" (float): The income threshold above which IETC begins to abate.
            - "ent" (float): The maximum IETC entitlement.
            - "abrate" (float): The abatement rate for IETC.

    Returns:
        float: The calculated IETC amount.
    """
    # IETC is not available to recipients of WFF, superannuation, or main benefits.
    if is_wff_recipient or is_super_recipient or is_benefit_recipient:
        return 0.0

    # Unpack IETC parameters for clarity.
    income_threshold_min = ietc_params["thrin"]
    income_threshold_max = ietc_params["thrab"]
    max_entitlement = ietc_params["ent"]
    abatement_rate = ietc_params["abrate"]

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
    tax_parameters: list[dict[str, list[float]]],
    base_year_average_weekly_earnings: float,
    base_year_earner_premium_rate: float,
    base_year_tax_parameters: dict[str, list[float]],
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
        tax_parameters (list[dict[str, list[float]]]): A list of 4 dictionaries, each containing
            the tax rates and thresholds for a simulation year.
        base_year_average_weekly_earnings (float): The average weekly earnings for the base year.
        base_year_earner_premium_rate (float): The earner premium rate for the base year.
        base_year_tax_parameters (dict): A dictionary containing the tax rates and thresholds for the base year.

    Returns:
        dict: A dictionary containing the calculated standard superannuation amounts.
    """
    results: dict[str, float] = {}

    # Base year
    base_year_super: float = base_year_average_weekly_earnings * 0.66 * 2
    base_year_net_super: float = netavg(
        base_year_super / 2,
        base_year_earner_premium_rate,
        base_year_tax_parameters["rates"],
        base_year_tax_parameters["thresholds"],
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
            tax_parameters[i]["rates"],
            tax_parameters[i]["thresholds"],
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
    family_boost_params: dict[str, float],
) -> float:
    """
    Calculates the FamilyBoost childcare tax credit.

    Args:
        family_income (float): The total family income.
        childcare_costs (float): The total childcare costs.
        family_boost_params (dict): A dictionary of FamilyBoost parameters
            (max_credit, income_threshold, abatement_rate, max_income).

    Returns:
        float: The calculated FamilyBoost credit.
    """
    max_credit = family_boost_params["max_credit"]
    income_threshold = family_boost_params["income_threshold"]
    abatement_rate = family_boost_params["abatement_rate"]
    max_income = family_boost_params["max_income"]

    if family_income > max_income:
        return 0.0

    credit = min(childcare_costs * 0.25, max_credit)

    if family_income > income_threshold:
        abatement = (family_income - income_threshold) * abatement_rate
        credit = max(0.0, credit - abatement)

    return credit
