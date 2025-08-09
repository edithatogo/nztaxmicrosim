from __future__ import annotations

from .parameters import (
    AccommodationSupplementParams,
    BSTCParams,
    ChildSupportParams,
    FTCParams,
    IWTCParams,
    JSSParams,
    MFTCParams,
    PPLParams,
    SLPParams,
    SPSParams,
    WEPParams,
)


def _apply_abatement(base: float, income: float, threshold: float, rate: float) -> float:
    """Apply income abatement to a benefit or entitlement.

    Abatement reduces the amount of a benefit or entitlement based on a
    person's income. If the income is above a certain threshold, the benefit
    is reduced by a certain rate for each dollar of income over the
    threshold.

    Args:
        base: The base amount of the benefit or entitlement.
        income: The income to test against the threshold.
        threshold: The income threshold at which abatement begins.
        rate: The rate at which the benefit is reduced.

    Returns:
        The abated amount of the benefit or entitlement.
    """
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
    """Calculate the Jobseeker Support (JSS) entitlement.

    JSS is a weekly payment for people who are not in full-time employment.
    The entitlement is based on the individual's income, marital status, and
    the number of dependent children.

    Args:
        individual_income: The individual's weekly income.
        is_single: Whether the individual is single.
        is_partnered: Whether the individual is partnered.
        num_dependent_children: The number of dependent children.
        jss_params: The parameters for JSS.

    Returns:
        The weekly JSS entitlement.
    """
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
    """Calculate the Sole Parent Support (SPS) entitlement.

    SPS is a weekly payment for single parents with dependent children. The
    entitlement is based on the individual's income and the number of
    dependent children.

    Args:
        individual_income: The individual's weekly income.
        num_dependent_children: The number of dependent children.
        sps_params: The parameters for SPS.

    Returns:
        The weekly SPS entitlement.
    """
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
    """Calculate the Supported Living Payment (SLP) entitlement.

    SLP is a weekly payment for people who have, or are caring for someone
    with, a significant health condition, injury, or disability. The
    entitlement is based on the individual's income, marital status, and
    disability status.

    Args:
        individual_income: The individual's weekly income.
        is_single: Whether the individual is single.
        is_partnered: Whether the individual is partnered.
        is_disabled: Whether the individual has a disability.
        slp_params: The parameters for SLP.

    Returns:
        The weekly SLP entitlement.
    """
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
    """Calculate the Accommodation Supplement entitlement.

    The Accommodation Supplement is a weekly payment that helps people with
    their rent, board, or mortgage payments. The entitlement is based on
    household income, housing costs, region, and the number of dependent
    children.

    Args:
        household_income: The total weekly income of the household.
        housing_costs: The weekly housing costs.
        region: The region where the household is located.
        num_dependent_children: The number of dependent children in the
            household.
        as_params: The parameters for the Accommodation Supplement.

    Returns:
        The weekly Accommodation Supplement entitlement.
    """
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
    """Calculate Paid Parental Leave (PPL) payments.

    PPL is a payment for eligible parents to help them take time off work to
    care for a new baby or a child under six who has come into their care.

    Args:
        weeks_taken: The number of weeks of PPL taken.
        ppl_params: The parameters for PPL.

    Returns:
        The total PPL payment.
    """
    if not ppl_params.enabled:
        return 0.0

    weeks = max(0, min(weeks_taken, ppl_params.max_weeks))
    return weeks * ppl_params.weekly_rate


def calculate_child_support(liable_income: float, cs_params: ChildSupportParams) -> float:
    """Calculate child support payments based on liable income.

    Child support is a payment made by a parent who does not live with their
    child to the parent or caregiver who does. This function calculates the
    amount of child support payable based on the liable parent's income.

    Args:
        liable_income: The liable parent's annual income.
        cs_params: The parameters for child support.

    Returns:
        The amount of child support payable.
    """
    if not cs_params.enabled:
        return 0.0

    return max(0.0, liable_income * cs_params.support_rate)


def calculate_wep(
    is_eligible: bool,
    is_single: bool,
    is_partnered: bool,
    num_dependent_children: int,
    wep_params: WEPParams,
) -> float:
    """Calculate the Winter Energy Payment (WEP) entitlement.

    The WEP is a payment to help with the cost of heating during the winter
    months. It is available to people receiving certain benefits or
    superannuation.

    Args:
        is_eligible: Whether the individual is eligible for the WEP.
        is_single: Whether the individual is single.
        is_partnered: Whether the individual is partnered.
        num_dependent_children: The number of dependent children.
        wep_params: The parameters for the WEP.

    Returns:
        The weekly WEP entitlement.
    """
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
    bstc_params: BSTCParams,
) -> float:
    """Calculate the Best Start Tax Credit (BSTC) entitlement.

    The BSTC is a payment for families with a new baby. It is designed to
    help with the costs of raising a child in their first few years. The
    entitlement is based on family income and the age of the youngest child.

    Args:
        family_income: The total annual family income.
        child_age: The age of the youngest child in years.
        bstc_params: The parameters for the BSTC.

    Returns:
        The annual BSTC entitlement.
    """
    if child_age > bstc_params.max_age:
        return 0.0

    base_rate = bstc_params.amount

    if child_age >= 1:
        return _apply_abatement(
            base_rate,
            family_income,
            bstc_params.threshold,
            bstc_params.rate,
        )
    return base_rate


def calculate_ftc(
    family_income: float,
    num_children: int,
    ftc_params: FTCParams,
) -> float:
    """Calculate the Family Tax Credit (FTC) entitlement.

    The FTC is a payment for families with dependent children. It is designed
    to help with the costs of raising a family. The entitlement is based on
    family income and the number of children.

    Args:
        family_income: The total annual family income.
        num_children: The number of dependent children.
        ftc_params: The parameters for the FTC.

    Returns:
        The annual FTC entitlement.
    """
    if num_children == 0:
        return 0.0

    base_rate = ftc_params.base_rate
    base_rate += (num_children - 1) * ftc_params.child_rate

    return _apply_abatement(
        base_rate,
        family_income,
        ftc_params.income_threshold,
        ftc_params.abatement_rate,
    )


def calculate_iwtc(
    family_income: float,
    num_children: int,
    hours_worked: int,
    iwtc_params: IWTCParams,
) -> float:
    """Calculate the In-Work Tax Credit (IWTC) entitlement.

    The IWTC is a payment for working families with dependent children. It is
    designed to help make work pay for low to middle-income families. The
    entitlement is based on family income, the number of children, and the
    hours worked.

    Args:
        family_income: The total annual family income.
        num_children: The number of dependent children.
        hours_worked: The number of hours worked per week.
        iwtc_params: The parameters for the IWTC.

    Returns:
        The annual IWTC entitlement.
    """
    if num_children == 0:
        return 0.0

    if hours_worked < iwtc_params.min_hours_worked:
        return 0.0

    base_rate = iwtc_params.base_rate
    base_rate += (num_children - 1) * iwtc_params.child_rate

    return _apply_abatement(
        base_rate,
        family_income,
        iwtc_params.income_threshold,
        iwtc_params.abatement_rate,
    )


def calculate_mftc(
    family_income: float,
    tax_paid: float,
    mftc_params: MFTCParams,
) -> float:
    """Calculate the Minimum Family Tax Credit (MFTC) entitlement.

    The MFTC is a payment for working families who would otherwise be better
    off on a benefit. It tops up their after-tax income to a guaranteed
    minimum amount.

    Args:
        family_income: The total annual family income.
        tax_paid: The amount of tax paid by the family.
        mftc_params: The parameters for the MFTC.

    Returns:
        The annual MFTC entitlement.
    """
    guaranteed_income = mftc_params.guaranteed_income
    net_income = family_income - tax_paid

    if net_income >= guaranteed_income:
        return 0.0

    return guaranteed_income - net_income
