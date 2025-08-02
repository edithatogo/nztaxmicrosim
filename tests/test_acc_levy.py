"""Unit tests for ACC levy calculations."""

from src.acc_levy import calculate_acc_levy, calculate_payroll_deductions
from src.microsim import taxit
from src.parameters import TaxBracketParams


def test_calculate_acc_levy():
    """Ensure levy is calculated correctly and capped at the maximum income."""
    assert calculate_acc_levy(50000, 0.012, 70000) == 50000 * 0.012
    assert calculate_acc_levy(80000, 0.012, 70000) == 70000 * 0.012
    assert calculate_acc_levy(-1000, 0.012, 70000) == 0.0


def test_calculate_payroll_deductions():
    """Combined deductions should equal income tax plus ACC levy."""
    tax_params = TaxBracketParams(rates=[0.10, 0.20], thresholds=[14000])
    income = 20000
    levy_rate = 0.012
    max_income = 70000
    expected_tax = taxit(income, tax_params)
    expected_levy = calculate_acc_levy(income, levy_rate, max_income)
    assert calculate_payroll_deductions(income, tax_params, levy_rate, max_income) == expected_tax + expected_levy
