"""ACC earner's levy calculations."""

from __future__ import annotations


def calculate_acc_levy(income: float, levy_rate: float, max_income: float) -> float:
    """Calculate the ACC earner's levy for a given income.

    The levy applies at a flat rate up to a maximum income. Income below zero
    results in no levy being charged.

    Args:
        income: Annual earnings subject to the levy.
        levy_rate: Levy percentage expressed as a decimal.
        max_income: Maximum income subject to the levy.

    Returns:
        The ACC levy owed.
    """
    if income <= 0 or levy_rate <= 0 or max_income <= 0:
        return 0.0

    chargeable_income = min(income, max_income)
    return chargeable_income * levy_rate


def calculate_payroll_deductions(
    income: float,
    rates: list[float],
    thresholds: list[float],
    levy_rate: float,
    levy_max_income: float,
) -> float:
    """Calculate total payroll deductions including income tax and ACC levy."""
    from .microsim import taxit

    income_tax = taxit(income, rates, thresholds)
    levy = calculate_acc_levy(income, levy_rate, levy_max_income)
    return income_tax + levy
