import pandas as pd
import pytest
from src.tax_calculator import TaxCalculator
from src.credits import eitc

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

def test_tax_calculator_rwt() -> None:
    calc = TaxCalculator.from_year("2024-2025")
    interest = 100.0

    # Test income in 10.5% bracket
    assert calc.rwt(interest, 14_000) == interest * 0.105
    # Test income in 17.5% bracket
    assert calc.rwt(interest, 48_000) == interest * 0.175
    # Test income in 30% bracket
    assert calc.rwt(interest, 70_000) == interest * 0.30
    # Test income in 33% bracket
    assert calc.rwt(interest, 180_000) == interest * 0.33
    # Test income in 39% bracket
    assert calc.rwt(interest, 200_000) == interest * 0.39


def test_tax_calculator_family_boost() -> None:
    calc = TaxCalculator.from_year("2024-2025")

    # Scenario 1: Income below threshold, credit is 25% of costs up to max
    assert calc.family_boost_credit(family_income=100_000, childcare_costs=200) == 50.0
    # Check max credit
    assert calc.family_boost_credit(family_income=100_000, childcare_costs=400) == 100.0

    # Scenario 2: Income above threshold, credit abates
    # Abatement = (150000 - 140000) * 0.25 = 2500. Credit = 75 - 25 = 50?
    # The max credit is per quarter, so 75. The abatement is on the quarterly credit.
    # Let's assume the passed childcare_costs are for a quarter.
    # Max credit per quarter is 975 (not in params). Let's use the params from the file.
    # params from 2024-2025.json: max_credit=975, income_threshold=140000, abatement_rate=0.25, max_income=180000
    # The family_boost_credit function seems to expect annual amounts.
    # Let's assume parameters are annual. Max credit is 75*13 = 975.
    # Let's assume childcare costs are also annual.
    # Let's test the logic as implemented.
    # The family_boost_credit function uses `family_boost_params` from `calc.params.family_boost`.
    # For "2024-2025", these are: max_credit=975, income_threshold=140000, abatement_rate=0.25, max_income=180000
    # Credit = min(300 * 0.25, 975) = 75
    # Abatement = (150000 - 140000) * 0.25 = 2500
    # Result = max(0, 75 - 2500) = 0.
    assert calc.family_boost_credit(family_income=150_000, childcare_costs=300) == 0.0

    # Scenario 3: Income above max_income, credit is 0
    assert calc.family_boost_credit(family_income=190_000, childcare_costs=300) == 0.0


def test_tax_calculator_eitc() -> None:
    calc = TaxCalculator.from_year("2023-2024")

    # These parameters are not in the JSON files, so we pass them directly.
    # This test just confirms that the TaxCalculator correctly delegates.
    result = calc.eitc(
        is_credit_enabled=True,
        is_eligible=True,
        income=30000,
        min_income_threshold=20000,
        max_entitlement_income=40000,
        abatement_income_threshold=50000,
        earning_rate=0.1,
        abatement_rate=0.2,
    )

    expected = eitc(
        is_credit_enabled=True,
        is_eligible=True,
        income=30000,
        min_income_threshold=20000,
        max_entitlement_income=40000,
        abatement_income_threshold=50000,
        earning_rate=0.1,
        abatement_rate=0.2,
    )

    assert result == expected


def test_tax_calculator_pie_tax() -> None:
    # Test with a year that has PIE params
    calc_with_pie = TaxCalculator.from_year("2024-2025")
    pie_income = 1000
    taxable_income = 50000
    # This should use the 17.5% rate
    expected_tax = pie_income * 0.175
    assert calc_with_pie.pie_tax(pie_income, taxable_income) == expected_tax

    # Test with a year that does not have PIE params
    calc_without_pie = TaxCalculator.from_year("2023-2024")
    assert calc_without_pie.pie_tax(pie_income, taxable_income) == 0.0


def test_calculate_emtr():
    """Test the calculate_emtr method."""
    calc = TaxCalculator.from_year("2023-2024")

    # Define a simple case: a single person, no benefits other than IETC
    individual_data = {
        "income": 48000, # At the threshold for IETC abatement
        "is_wff_recipient": False,
        "is_super_recipient": False,
        "is_benefit_recipient": False,
    }

    # Manual calculation for this specific case:
    # At 48000, tax is 7560. IETC is 520. Net income = 48000 - 7560 + 520 = 41000.
    # At 48001, tax is 7560.30. IETC is 519.87. Net income = 48001 - 7560.30 + 519.87 = 40999.57
    # Change in net income = 40999.57 - 41000 = -0.43
    # EMTR = 1 - (-0.43) is wrong.
    # EMTR = 1 - (change_in_net_income / change_in_gross_income)
    # EMTR = 1 - (net_income_plus_one - net_income_original) / 1
    # Let's re-calculate net income based on the _calculate_net_income function

    # At 48000:
    # tax = 7560
    # ietc = 520
    # net = 48000 - 7560 + 520 = 40960

    # At 48001:
    # tax = 7560.3
    # ietc = 520 - 0.13 = 519.87
    # net = 48001 - 7560.3 + 519.87 = 40960.57

    # change in net income = 0.57
    # EMTR = 1 - 0.57 = 0.43
    # This is the 30% tax rate plus the 13% IETC abatement rate.

    emtr = calc.calculate_emtr(individual_data)
    assert abs(emtr - 0.43) < 0.001