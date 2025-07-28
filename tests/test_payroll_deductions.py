"""Unit tests for payroll deduction helpers."""

from src.payroll_deductions import (
    calculate_kiwisaver_contribution,
    calculate_student_loan_repayment,
)


def test_calculate_kiwisaver_contribution():
    rate = 0.03
    assert calculate_kiwisaver_contribution(50000, rate) == 1500.0
    assert calculate_kiwisaver_contribution(0, rate) == 0.0
    assert calculate_kiwisaver_contribution(-1000, rate) == 0.0


def test_calculate_student_loan_repayment():
    threshold = 20000
    rate = 0.12
    assert calculate_student_loan_repayment(15000, threshold, rate) == 0.0
    assert calculate_student_loan_repayment(50000, threshold, rate) == (50000 - threshold) * rate
