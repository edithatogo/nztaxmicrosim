from typing import Any


def calculate_jss(
    individual_income: float,
    is_single: bool,
    is_partnered: bool,
    num_dependent_children: int,
    jss_params: dict[str, Any],
) -> float:
    """
    Calculates the Jobseeker Support (JSS) entitlement for an individual.

    Args:
        individual_income (float): The individual's weekly income.
        is_single (bool): True if the individual is single.
        is_partnered (bool): True if the individual is partnered.
        num_dependent_children (int): Number of dependent children.
        jss_params (dict): A dictionary of JSS parameters, including:
            - "single_rate" (float): The weekly rate for a single person.
            - "couple_rate" (float): The weekly rate for a couple (per person).
            - "child_rate" (float): Additional weekly rate per child (if applicable).
            - "income_abatement_threshold" (float): Income threshold before abatement.
            - "abatement_rate" (float): Rate at which JSS abates with income.

    Returns:
        float: The calculated weekly JSS amount.
    """
    base_rate = 0.0
    if is_single:
        base_rate = jss_params["single_rate"]
    elif is_partnered:
        base_rate = jss_params["couple_rate"]

    # Add child rate if applicable
    base_rate += num_dependent_children * jss_params.get("child_rate", 0.0)

    # Apply abatement
    if individual_income > jss_params["income_abatement_threshold"]:
        abatement = (individual_income - jss_params["income_abatement_threshold"]) * jss_params["abatement_rate"]
        return max(0.0, base_rate - abatement)
    return base_rate


def calculate_sps(
    individual_income: float,
    num_dependent_children: int,
    sps_params: dict[str, Any],
) -> float:
    """
    Calculates the Sole Parent Support (SPS) entitlement for an individual.

    Args:
        individual_income (float): The individual's weekly income.
        num_dependent_children (int): Number of dependent children.
        sps_params (dict): A dictionary of SPS parameters, including:
            - "base_rate" (float): The weekly base rate for a sole parent.
            - "income_abatement_threshold" (float): Income threshold before abatement.
            - "abatement_rate" (float): Rate at which SPS abates with income.

    Returns:
        float: The calculated weekly SPS amount.
    """
    if num_dependent_children == 0:
        return 0.0

    base_rate = sps_params["base_rate"]

    if individual_income > sps_params["income_abatement_threshold"]:
        abatement = (individual_income - sps_params["income_abatement_threshold"]) * sps_params["abatement_rate"]
        return max(0.0, base_rate - abatement)
    return base_rate


def calculate_slp(
    individual_income: float,
    is_single: bool,
    is_partnered: bool,
    is_disabled: bool,
    slp_params: dict[str, Any],
) -> float:
    """
    Calculates the Supported Living Payment (SLP) entitlement for an individual.

    Args:
        individual_income (float): The individual's weekly income.
        is_single (bool): True if the individual is single.
        is_partnered (bool): True if the individual is partnered.
        is_disabled (bool): True if the individual has a disability.
        slp_params (dict): A dictionary of SLP parameters, including:
            - "single_rate" (float): The weekly rate for a single person.
            - "couple_rate" (float): The weekly rate for a couple (per person).
            - "income_abatement_threshold" (float): Income threshold before abatement.
            - "abatement_rate" (float): Rate at which SLP abates with income.

    Returns:
        float: The calculated weekly SLP amount.
    """
    if not is_disabled:
        return 0.0

    base_rate = 0.0
    if is_single:
        base_rate = slp_params["single_rate"]
    elif is_partnered:
        base_rate = slp_params["couple_rate"]

    if individual_income > slp_params["income_abatement_threshold"]:
        abatement = (individual_income - slp_params["income_abatement_threshold"]) * slp_params["abatement_rate"]
        return max(0.0, base_rate - abatement)
    return base_rate


def calculate_accommodation_supplement(
    household_income: float,
    housing_costs: float,
    region: str,
    num_dependent_children: int,
    as_params: dict[str, Any],
) -> float:
    """
    Calculates the Accommodation Supplement (AS) entitlement for a household.

    Args:
        household_income (float): The household's weekly income.
        housing_costs (float): The household's weekly housing costs (rent/mortgage).
        region (str): The region of the household (e.g., "Auckland", "Wellington").
        num_dependent_children (int): Number of dependent children in the household.
        as_params (dict): A dictionary of AS parameters, including:
            - "income_thresholds" (dict): Income thresholds by family type.
            - "abatement_rate" (float): Rate at which AS abates with income.
            - "max_entitlement_rates" (dict): Max AS entitlement by region and family type.
            - "housing_cost_contribution_rate" (float): Rate at which housing costs contribute to AS.
            - "housing_cost_threshold" (float): Housing cost threshold before AS applies.

    Returns:
        float: The calculated weekly Accommodation Supplement amount.
    """
    # Determine family type for AS parameters
    family_type = "single_no_children"
    if num_dependent_children > 0:
        family_type = "with_children"
    # This is a simplification; actual AS has more granular family types

    income_threshold = as_params["income_thresholds"].get(family_type, 0.0)
    max_entitlement = as_params["max_entitlement_rates"].get(region, {}).get(family_type, 0.0)

    # Calculate initial entitlement based on housing costs
    initial_entitlement = max(
        0.0, (housing_costs - as_params["housing_cost_threshold"]) * as_params["housing_cost_contribution_rate"]
    )
    initial_entitlement = min(initial_entitlement, max_entitlement)

    # Apply abatement based on household income
    if household_income > income_threshold:
        abatement = (household_income - income_threshold) * as_params["abatement_rate"]
        return max(0.0, initial_entitlement - abatement)
    return initial_entitlement
