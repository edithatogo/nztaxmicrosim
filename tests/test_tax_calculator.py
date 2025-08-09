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
        rwt_rate_10_5=0.1,
        rwt_rate_17_5=0.2,
        rwt_rate_30=0.3,
        rwt_rate_33=0.4,
        rwt_rate_39=0.5,
    )
    assert calc.rwt(interest, rwt_params=custom_rwt_params) == simrwt(interest, custom_rwt_params)


