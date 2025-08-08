<<<<<<< HEAD
from src.microsim import calcietc, load_parameters, simrwt, taxit
<<<<<<< HEAD
=======
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
    params = load_parameters("2023-2024")
    calc = TaxCalculator(params)
    interest = 100.0
    # Test with default parameters
    assert calc.rwt(interest) == simrwt(interest, calc.params.rwt)

    # Test with custom parameters
    custom_params = RWTParams(0.1, 0.2, 0.3, 0.33, 0.39)
    assert calc.rwt(interest, custom_params) == simrwt(interest, custom_params)
