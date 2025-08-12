import pandas as pd
import pytest
from src.tax_calculator import TaxCalculator

@pytest.fixture
def tax_calculator():
    # Example parameters for a fictional tax system for testing purposes
    tax_brackets = {
        "rates": [0.105, 0.175, 0.30, 0.33, 0.39],
        "thresholds": [0, 14000, 48000, 70000, 180000]
    }
    return TaxCalculator(tax_brackets)

def test_calculate_tax(tax_calculator):
    # Test with a simple case
    assert tax_calculator.calculate_tax(50000) == 8020.0

def test_calculate_tax_edge_cases(tax_calculator):
    # Test boundaries of tax brackets
    assert tax_calculator.calculate_tax(14000) == 1470.0
    assert tax_calculator.calculate_tax(48000) == 8020.0
    assert tax_calculator.calculate_tax(70000) == 14020.0
    assert tax_calculator.calculate_tax(180000) == 49920.0

def test_calculate_tax_with_zero_income(tax_calculator):
    # Test zero income
    assert tax_calculator.calculate_tax(0) == 0.0

def test_calculate_tax_with_high_income(tax_calculator):
    # Test high income
    assert tax_calculator.calculate_tax(250000) == 77220.0

def test_calculate_tax_with_dataframe(tax_calculator):
    # Test with a pandas DataFrame
    data = {'income': [50000, 14000, 70000, 0, 250000]}
    df = pd.DataFrame(data)
    expected_tax = pd.Series([8020.0, 1470.0, 14020.0, 0.0, 77220.0])
    pd.testing.assert_series_equal(tax_calculator.calculate_tax(df['income']), expected_tax, check_names=False)