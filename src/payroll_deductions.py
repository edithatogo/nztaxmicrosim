"""Helper functions for payroll deductions."""

from __future__ import annotations


def calculate_kiwisaver_contribution(income: float, rate: float) -> float:
    """
    Calculate the employee's KiwiSaver contribution.

    KiwiSaver is a voluntary savings scheme to help New Zealanders save for
    their retirement. This function calculates the employee's contribution
    based on their income and a specified contribution rate.

    Args:
        income: The annual income subject to KiwiSaver contributions.
        rate: The contribution rate, expressed as a decimal (e.g., 0.03 for 3%).

    Returns:
        The calculated KiwiSaver contribution. Returns 0.0 for negative or
        zero income or rate.
    """
    if income <= 0 or rate <= 0:
        return 0.0
    return income * rate


def calculate_student_loan_repayment(income: float, repayment_threshold: float, repayment_rate: float) -> float:
    """
    Calculate the mandatory student loan repayment for a given income.

    This function calculates the amount of student loan repayment required
    based on an individual's income. Repayments are only required if the
    income is above a certain threshold.

    Args:
        income: The annual taxable income.
        repayment_threshold: The income threshold above which repayments apply.
        repayment_rate: The rate applied to income above the threshold,
            expressed as a decimal.

    Returns:
        The calculated student loan repayment amount.
    """
    if income <= repayment_threshold or repayment_rate <= 0:
        return 0.0
    return (income - repayment_threshold) * repayment_rate
