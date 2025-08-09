from src.microsim import calcietc, simrwt, taxit
from src.parameters import RWTParams
from src.tax_calculator import TaxCalculator


def test_tax_calculator_income_tax_and_ietc() -> None:
    calc = TaxCalculator.from_year("2023-2024")
    income = 50_000
    expected_tax = taxit(income, calc.params.tax_brackets)
    assert calc.income_tax(income) == expected_tax

    expected_ietc = calcietc(
        taxable_income=30_000,
        is_wff_recipient=False,
        is_super_recipient=False,
        is_benefit_recipient=False,
        ietc_params=calc.params.ietc,
    )
    assert (
        calc.ietc(
            taxable_income=30_000,
            is_wff_recipient=False,
            is_super_recipient=False,
            is_benefit_recipient=False,
        )
        == expected_ietc
    )


def test_tax_calculator_rwt_delegates() -> None:
    calc = TaxCalculator.from_year("2023-2024")
    interest = 100.0
    # Test with default parameters
    assert calc.rwt(interest) == simrwt(interest, calc.params.rwt)


def test_tax_calculator_rwt_with_custom_params() -> None:
    calc = TaxCalculator.from_year("2023-2024")
    interest = 100.0
    # Test with custom parameters
    custom_rwt_params = RWTParams(
        rwt_rate_1=0.1,
        rwt_rate_2=0.2,
        rwt_rate_3=0.3,
        rwt_rate_4=0.4,
        rwt_thresh_1=1000,
        rwt_thresh_2=2000,
        rwt_thresh_3=3000,
    )
    assert calc.rwt(interest, custom_rwt_params) == simrwt(interest, custom_rwt_params)


def test_tax_calculator_rwt_with_custom_rate() -> None:
    calc = TaxCalculator.from_year("2023-2024")
    interest = 100.0
    # Test with a custom rate
    assert calc.rwt(interest, rwt_rate=0.5) == simrwt(interest, calc.params.rwt, rwt_rate=0.5)


def test_tax_calculator_rwt_with_custom_params_and_rate() -> None:
    calc = TaxCalculator.from_year("2023-2024")
    interest = 100.0
    # Test with custom parameters and a custom rate
    custom_rwt_params = RWTParams(
        rwt_rate_1=0.1,
        rwt_rate_2=0.2,
        rwt_rate_3=0.3,
        rwt_rate_4=0.4,
        rwt_thresh_1=1000,
        rwt_thresh_2=2000,
        rwt_thresh_3=3000,
    )
    assert calc.rwt(interest, custom_rwt_params, rwt_rate=0.5) == simrwt(interest, custom_rwt_params, rwt_rate=0.5)