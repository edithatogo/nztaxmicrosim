"""Tests for the tax rules."""

import pandas as pd

from src.microsim import load_parameters
from src.tax_calculator import TaxCalculator
from src.tax_rules import ACCLevyRule, IETCRule, IncomeTaxRule, KiwiSaverRule, StudentLoanRule


def test_acc_levy_rule():
    """Test the ACCLevyRule."""
    rule = ACCLevyRule()
    params = load_parameters("2023-2024")
    data = {
        "df": pd.DataFrame({"familyinc": [50000, 150000]}),
        "params": params,
    }
    rule(data)
    assert "acc_levy" in data["df"].columns
    assert data["df"]["acc_levy"][0] == 765
    assert data["df"]["acc_levy"][1] == 139111 * 0.0153


def test_kiwisaver_rule():
    """Test the KiwiSaverRule."""
    rule = KiwiSaverRule()
    params = load_parameters("2023-2024")
    data = {
        "df": pd.DataFrame({"familyinc": [50000, 150000]}),
        "params": params,
    }
    rule(data)
    assert "kiwisaver_contribution" in data["df"].columns
    assert data["df"]["kiwisaver_contribution"][0] == 1500
    assert data["df"]["kiwisaver_contribution"][1] == 4500


def test_student_loan_rule():
    """Test the StudentLoanRule."""
    rule = StudentLoanRule()
    params = load_parameters("2023-2024")
    data = {
        "df": pd.DataFrame({"familyinc": [50000, 150000]}),
        "params": params,
    }
    rule(data)
    assert "student_loan_repayment" in data["df"].columns
    assert data["df"]["student_loan_repayment"][0] == (50000 - 22828) * 0.12
    assert data["df"]["student_loan_repayment"][1] == (150000 - 22828) * 0.12


def test_ietc_rule():
    """Test the IETCRule."""
    rule = IETCRule()
    params = load_parameters("2023-2024")
    tax_calc = TaxCalculator(params=params)
    data = {
        "df": pd.DataFrame(
            {
                "familyinc": [20000, 30000, 50000],
                "FTCcalc": [0, 0, 100],
                "is_nz_super_recipient": [False, False, False],
                "is_jss_recipient": [False, False, False],
                "is_sps_recipient": [False, False, False],
                "is_slp_recipient": [False, False, False],
            }
        ),
        "params": params,
        "tax_calc": tax_calc,
    }
    rule(data)
    df = data["df"]
    assert "ietc" in df.columns
    assert df["ietc"][0] == 0
    assert df["ietc"][1] == 520
    assert df["ietc"][2] == 0


def test_income_tax_rule():
    """Test the IncomeTaxRule."""
    rule = IncomeTaxRule()
    params = load_parameters("2023-2024")
    tax_calc = TaxCalculator(params=params)
    data = {
        "df": pd.DataFrame({"familyinc": [50000, 150000]}),
        "params": params,
        "tax_calc": tax_calc,
    }
    rule(data)
    assert "tax_liability" in data["df"].columns
    assert data["df"]["tax_liability"][0] == 8020.0
    assert data["df"]["tax_liability"][1] == 40420.0
