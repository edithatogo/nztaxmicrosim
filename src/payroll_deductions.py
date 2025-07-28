"""Helper functions for payroll deductions."""

from __future__ import annotations


def calculate_kiwisaver_contribution(income: float, rate: float) -> float:
    """Return KiwiSaver contribution at the given rate.

    Args:
        income: Annual income subject to KiwiSaver contributions.
        rate: Contribution rate expressed as a decimal (e.g. ``0.03`` for 3%).

    Returns:
        Calculated contribution. Negative incomes yield ``0.0``.
    """
    if income <= 0 or rate <= 0:
        return 0.0
    return income * rate


def calculate_student_loan_repayment(income: float, repayment_threshold: float, repayment_rate: float) -> float:
    """Return mandatory student loan repayment for a given income.

    Args:
        income: Annual taxable income.
        repayment_threshold: Income threshold above which repayments apply.
        repayment_rate: Rate applied to income above the threshold.

    Returns:
        The calculated repayment amount.
    """
    if income <= repayment_threshold or repayment_rate <= 0:
        return 0.0
    return (income - repayment_threshold) * repayment_rate
