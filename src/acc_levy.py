"""ACC earner's levy calculations."""

from __future__ import annotations

from .parameters import TaxBracketParams


def calculate_acc_levy(income: float, levy_rate: float, max_income: float) -> float:
    """
    Calculate the ACC (Accident Compensation Corporation) earner's levy.

    The ACC earner's levy is a compulsory payment that helps fund the cost of
    accidents in New Zealand. It is calculated as a flat rate on income up to
    a specified maximum.

    Args:
        income: The annual earnings subject to the levy.
        levy_rate: The ACC levy rate, expressed as a decimal (e.g., 1.46%
            is 0.0146).
        max_income: The maximum income on which the levy is charged.

    Returns:
        The total ACC levy owed for the year.
    """
    if income <= 0 or levy_rate <= 0 or max_income <= 0:
        return 0.0

    chargeable_income = min(income, max_income)
    return chargeable_income * levy_rate


def calculate_payroll_deductions(
    income: float,
    tax_params: "TaxBracketParams",
    levy_rate: float,
    levy_max_income: float,
) -> float:
    """
    Calculate total payroll deductions, including income tax and ACC levy.

    This function provides a combined calculation of the two main deductions
    from an individual's income: income tax and the ACC earner's levy.

    Args:
        income: The annual income.
        tax_params: The tax bracket parameters for the income tax calculation.
        levy_rate: The ACC levy rate.
        levy_max_income: The maximum income for the ACC levy.

    Returns:
        The total amount of payroll deductions.
    """
    from .microsim import taxit

    income_tax = taxit(income, tax_params)
    levy = calculate_acc_levy(income, levy_rate, levy_max_income)
    return income_tax + levy
