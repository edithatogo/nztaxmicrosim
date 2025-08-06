from __future__ import annotations

from .parameters import (
    AccommodationSupplementParams,
    ChildSupportParams,
    JSSParams,
    PPLParams,
    SLPParams,
    SPSParams,
)


def _apply_abatement(base: float, income: float, threshold: float, rate: float) -> float:
    """Apply income abatement to a benefit or entitlement."""

    if income > threshold:
        abatement = (income - threshold) * rate
        return max(0.0, base - abatement)
    return base


def calculate_jss(
    individual_income: float,
    is_single: bool,
    is_partnered: bool,
    num_dependent_children: int,
    jss_params: JSSParams,
) -> float:
    """Calculate the Jobseeker Support (JSS) entitlement."""

    base_rate = 0.0
    if is_single:
        base_rate = jss_params.single_rate
    elif is_partnered:
        base_rate = jss_params.couple_rate
    base_rate += num_dependent_children * jss_params.child_rate

    if individual_income > jss_params.income_abatement_threshold:
        abatement = (individual_income - jss_params.income_abatement_threshold) * jss_params.abatement_rate
        return max(0.0, base_rate - abatement)
    return base_rate


def calculate_sps(
    individual_income: float,
    num_dependent_children: int,
    sps_params: SPSParams,
) -> float:
    """Calculate the Sole Parent Support (SPS) entitlement."""

    if num_dependent_children == 0:
        return 0.0

    base_rate = sps_params.base_rate
    if individual_income > sps_params.income_abatement_threshold:
        abatement = (individual_income - sps_params.income_abatement_threshold) * sps_params.abatement_rate
        return max(0.0, base_rate - abatement)
    return base_rate


def calculate_slp(
    individual_income: float,
    is_single: bool,
    is_partnered: bool,
    is_disabled: bool,
    slp_params: SLPParams,
) -> float:
    """Calculate the Supported Living Payment (SLP) entitlement."""

    if not is_disabled:
        return 0.0

    base_rate = 0.0
    if is_single:
        base_rate = slp_params.single_rate
    elif is_partnered:
        base_rate = slp_params.couple_rate

    if individual_income > slp_params.income_abatement_threshold:
        abatement = (individual_income - slp_params.income_abatement_threshold) * slp_params.abatement_rate
        return max(0.0, base_rate - abatement)
    return base_rate


def calculate_accommodation_supplement(
    household_income: float,
    housing_costs: float,
    region: str,
    num_dependent_children: int,
    as_params: AccommodationSupplementParams,
) -> float:
    """Calculate the Accommodation Supplement entitlement."""

    family_type = "single_no_children"
    if num_dependent_children > 0:
        family_type = "with_children"

    income_threshold = as_params.income_thresholds.get(family_type, 0.0)
    max_entitlement = as_params.max_entitlement_rates.get(region, {}).get(family_type, 0.0)

    initial_entitlement = max(
        0.0, (housing_costs - as_params.housing_cost_threshold) * as_params.housing_cost_contribution_rate
    )
    initial_entitlement = min(initial_entitlement, max_entitlement)

    if household_income > income_threshold:
        abatement = (household_income - income_threshold) * as_params.abatement_rate
        return max(0.0, initial_entitlement - abatement)
    return initial_entitlement


def calculate_ppl(weeks_taken: int, ppl_params: PPLParams) -> float:
    """Calculate Paid Parental Leave payments."""

    if not ppl_params.enabled:
        return 0.0

    weeks = max(0, min(weeks_taken, ppl_params.max_weeks))
    return weeks * ppl_params.weekly_rate


def calculate_child_support(liable_income: float, cs_params: ChildSupportParams) -> float:
    """Calculate child support payments based on liable income."""

    if not cs_params.enabled:
        return 0.0

    return max(0.0, liable_income * cs_params.support_rate)


def calculate_wep(
    is_eligible: bool,
    is_single: bool,
    is_partnered: bool,
    num_dependent_children: int,
    wep_params: "WEPParams",
) -> float:
    """Calculate the Winter Energy Payment (WEP) entitlement."""

    if not is_eligible:
        return 0.0

    base_rate = 0.0
    if is_single:
        base_rate = wep_params.single_rate
    elif is_partnered:
        base_rate = wep_params.couple_rate
    base_rate += num_dependent_children * wep_params.child_rate

    return base_rate


def calculate_bstc(
    family_income: float,
    child_age: int,
    bstc_params: "BSTCParams",
) -> float:
    """Calculate the Best Start Tax Credit (BSTC) entitlement."""

    if child_age > bstc_params.max_age:
        return 0.0

    base_rate = bstc_params.base_rate

    if child_age >= 1:
        return _apply_abatement(
            base_rate,
            family_income,
            bstc_params.income_threshold,
            bstc_params.abatement_rate,
        )
    return base_rate
