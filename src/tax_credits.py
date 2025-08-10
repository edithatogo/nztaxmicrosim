from __future__ import annotations

from typing import Any, Mapping

from .parameters import FamilyBoostParams, IETCParams


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
