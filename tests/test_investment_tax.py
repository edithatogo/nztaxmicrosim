from __future__ import annotations

import pytest

from src.investment_tax import calculate_pie_tax
from src.parameters import PIEParams


@pytest.fixture
def pie_params() -> PIEParams:
    """Returns a default set of PIE parameters for testing."""
    return PIEParams(
        rates=[0.105, 0.175, 0.28],
        taxable_income_thresholds=[15600, 53500],
        taxable_plus_pie_income_thresholds=[53500, 78100],
    )


def test_calculate_pie_tax_rate_10_5(pie_params: PIEParams):
    """Test PIE tax calculation for the 10.5% PIR."""
    # Taxable income <= 15600 and total income <= 53500
    pie_income = 1000
    taxable_income = 15000
    expected_tax = pie_income * 0.105
    assert calculate_pie_tax(pie_income, taxable_income, pie_params) == expected_tax


def test_calculate_pie_tax_rate_17_5(pie_params: PIEParams):
    """Test PIE tax calculation for the 17.5% PIR."""
    # Taxable income <= 53500 and total income <= 78100
    pie_income = 1000
    taxable_income = 50000
    expected_tax = pie_income * 0.175
    assert calculate_pie_tax(pie_income, taxable_income, pie_params) == expected_tax


def test_calculate_pie_tax_rate_28(pie_params: PIEParams):
    """Test PIE tax calculation for the 28% PIR."""
    # Taxable income > 53500
    pie_income = 1000
    taxable_income = 60000
    expected_tax = pie_income * 0.28
    assert calculate_pie_tax(pie_income, taxable_income, pie_params) == expected_tax

    # Total income > 78100
    pie_income = 1000
    taxable_income = 78000
    expected_tax = pie_income * 0.28
    assert calculate_pie_tax(pie_income, taxable_income, pie_params) == expected_tax


def test_calculate_pie_tax_zero_income(pie_params: PIEParams):
    """Test PIE tax with zero income."""
    assert calculate_pie_tax(0, 50000, pie_params) == 0


def test_calculate_pie_tax_negative_income(pie_params: PIEParams):
    """Test PIE tax with negative income."""
    assert calculate_pie_tax(-1000, 50000, pie_params) == 0
