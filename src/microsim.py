import json
from typing import Any


def load_parameters(year: str) -> dict[str, Any]:
    """
    Loads tax parameters from a JSON file for a specific year.

    Args:
        year (str): The year for which to load the parameters (e.g., "2023-2024").

    Returns:
        dict: A dictionary containing the tax parameters.
    """
    with open("src/parameters.json", "r") as f:
        all_params = json.load(f)
    return all_params[year]


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
    taxy: float,
    parmflag: str,
    wffamt: float,
    supamt: float,
    benamt: float,
    ietc_params: dict[str, float],
    ietc0: float,
    taxinc0: float,
) -> float:
    """
    Calculates the Independent Earner Tax Credit (IETC).

    This function replicates the logic of the SAS macro `%calcietc`.

    Args:
        taxy (float): The taxable income.
        parmflag (str): A flag to indicate if the parameter is 'ys'.
        wffamt (float): The Working for Families amount.
        supamt (float): The superannuation amount.
        benamt (float): The benefit amount.
        ietc_params (dict): A dictionary of IETC parameters.
        ietc0 (float): The previous IETC amount.
        taxinc0 (float): The previous taxable income.

    Returns:
        float: The calculated IETC.
    """
    cietc: float = 0.0
    if parmflag == "ys":
        iposs: int = 0
        if ietc0 != 0:
            iposs = 1

        if wffamt == 0 and supamt == 0 and benamt == 0:
            icore: float = 0.0
            if taxinc0 <= 24000:
                icore = 0.0
            elif taxinc0 <= 44000:
                icore = 520.0
            else:
                icore = max(0.0, 520.0 - 0.13 * (taxinc0 - 44000))

            if icore > 0 and ietc0 > 0:
                iposs = 1
            elif icore > 0 and ietc0 == 0:
                iposs = 0
            elif icore == 0 and ietc0 > 0:
                iposs = 1
            elif icore == 0 and ietc0 == 0:
                iposs = 1

        if iposs == 1:
            if taxy <= ietc_params["thrin"]:
                cietc = 0.0
            elif taxy <= ietc_params["thrab"]:
                cietc = ietc_params["ent"]
            else:
                cietc = max(0.0, ietc_params["ent"] - ietc_params["abrate"] * (taxy - ietc_params["thrab"]))
    return cietc


def eitc(
    credflag: int,
    eligflag: int,
    incvar: float,
    thrin: float,
    par1: float,
    par2: float,
    earnrt: float,
    abrt: float,
) -> float:
    """
    Calculates the Earned Income Tax Credit (EITC).

    This function replicates the logic of the SAS macro `%eitc`.

    Args:
        credflag (int): A flag to indicate if the credit is on or off.
        eligflag (int): A flag to indicate if the person is eligible.
        incvar (float): The income variable.
        thrin (float): The income threshold to be eligible.
        par1 (float): The income point at which the maximum entitlement is first attained.
        par2 (float): The income point at which the entitlement starts to abate.
        earnrt (float): The rate at which the credit is earned.
        abrt (float): The rate at which the credit is abated.

    Returns:
        float: The calculated EITC.
    """
    outcred: float = 0.0
    if credflag == 1 and eligflag == 1:
        if incvar <= thrin:
            outcred = 0.0
        elif incvar <= par1:
            outcred = earnrt * (incvar - thrin)
        elif incvar <= par2:
            outcred = (par1 - thrin) * earnrt
        else:
            outcred = max(0.0, (par1 - thrin) * earnrt - (incvar - par2) * abrt)
    return outcred


def simrwt(
    interest: float,
    lowr1: float,
    lowr2: float,
    hir1: float,
    hir2: float,
    hir3: float,
) -> float:
    """
    Simulates the Resident Withholding Tax (RWT).

    This function replicates the logic of the SAS macro `%simrwt`.

    Args:
        interest (float): The interest income.
        lowr1 (float): The lower rate 1.
        lowr2 (float): The lower rate 2.
        hir1 (float): The higher rate 1.
        hir2 (float): The higher rate 2.
        hir3 (float): The higher rate 3.

    Returns:
        float: The calculated RWT.
    """
    if interest <= 0:
        return 0.0
    else:
        outtax: float = interest * (0.0 + 1.05 * lowr1 + 1.75 * lowr2 + 0.30 * hir1 + 0.33 * hir2 + 0.39 * hir3)
        return min(interest, outtax)


def supstd(
    cpi_factors: list[float],
    awe: list[float],
    ep: list[float],
    fl: list[float],
    tax_params: list[dict[str, list[float]]],
    awe22: float,
    ep_base: float,
    tax_params_base: dict[str, list[float]],
) -> dict[str, float]:
    """
    Calculates standard superannuation.

    This function replicates the logic of the SAS macro `%supstd`.

    Args:
        cpi_factors (list): A list of 4 CPI factors for the simulation years.
        awe (list): A list of 4 average weekly earnings for the simulation years.
        ep (list): A list of 4 earner premium rates for the simulation years.
        fl (list): A list of 4 superannuation accord floor relativities for the simulation years.
        tax_params (list): A list of 4 dictionaries, each containing the tax rates and thresholds for a simulation year.
        awe22 (float): The average weekly earnings for the base year.
        ep_base (float): The earner premium rate for the base year.
        tax_params_base (dict): A dictionary containing the tax rates and thresholds for the base year.

    Returns:
        dict: A dictionary containing the calculated standard superannuation amounts.
    """
    results: dict[str, float] = {}

    # Base year
    std22: float = awe22 * 0.66 * 2
    stdnet22: float = netavg(std22 / 2, ep_base, tax_params_base["rates"], tax_params_base["thresholds"])
    results["std22"] = std22
    results["stdnet22"] = stdnet22

    # Simulation years
    std_values: list[float] = []
    stdnet_values: list[float] = []

    std_prev: float = std22
    for i in range(4):
        std: float = max(awe[i] * fl[i] * 2, std_prev * cpi_factors[i])
        stdnet: float = netavg(std / 2, ep[i], tax_params[i]["rates"], tax_params[i]["thresholds"])
        std_values.append(std)
        stdnet_values.append(stdnet)
        std_prev = std

    results["std"] = std_values[0]
    results["stdnet"] = stdnet_values[0]
    results["std1"] = std_values[1]
    results["stdnet1"] = stdnet_values[1]
    results["std2"] = std_values[2]
    results["stdnet2"] = stdnet_values[2]
    results["std3"] = std_values[3]
    results["stdnet3"] = stdnet_values[3]

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
        family_boost_params (dict): A dictionary of FamilyBoost parameters.

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
