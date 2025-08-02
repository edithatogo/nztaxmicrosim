from src.microsim import calcietc, simrwt, taxit
from src.tax_calculator import TaxCalculator


def test_tax_calculator_income_tax_and_ietc() -> None:
    calc = TaxCalculator.from_year("2023-2024")
    income = 50_000
    expected_tax = taxit(income, calc.params["tax_brackets"]["rates"], calc.params["tax_brackets"]["thresholds"])
    assert calc.income_tax(income) == expected_tax

    expected_ietc = calcietc(
        taxable_income=30_000,
        is_wff_recipient=False,
        is_super_recipient=False,
        is_benefit_recipient=False,
        ietc_params=calc.params["ietc"],
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
    params = {
        "tax_brackets": {"rates": [0.1], "thresholds": [1_000]},
        "ietc": {"thrin": 0, "ent": 0, "thrab": 0, "abrate": 0},
        "rwt": {
            "rwt_rate_10_5": 0.1,
            "rwt_rate_17_5": 0.2,
            "rwt_rate_30": 0.3,
            "rwt_rate_33": 0.33,
            "rwt_rate_39": 0.39,
        },
    }
    calc = TaxCalculator(params)
    interest = 100.0
    expected = simrwt(interest, 0.1, 0.2, 0.3, 0.33, 0.39)
    assert calc.rwt(interest) == expected
