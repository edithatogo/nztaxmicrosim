"""Tests for the tax rules."""

import pandas as pd

from src.parameters import ACCLevyParams, KiwisaverParams, StudentLoanParams
from src.tax_rules import ACCLevyRule, KiwiSaverRule, StudentLoanRule


def test_acc_levy_rule():
    """Test the ACCLevyRule."""
    rule = ACCLevyRule(
        acc_levy_params=ACCLevyParams(rate=0.0153, max_income=139111)
    )
    data = {
        "df": pd.DataFrame(
            {
                "familyinc": [50000, 150000],
            }
        )
    }
    rule(data)
    assert "acc_levy" in data["df"].columns
    assert data["df"]["acc_levy"][0] == 765
    assert data["df"]["acc_levy"][1] == 139111 * 0.0153


from src.parameters import StudentLoanParams


def test_kiwisaver_rule():
    """Test the KiwiSaverRule."""
    rule = KiwiSaverRule(
        kiwisaver_params=KiwisaverParams(contribution_rate=0.03)
    )
    data = {
        "df": pd.DataFrame(
            {
                "familyinc": [50000, 150000],
            }
        )
    }
    rule(data)
    assert "kiwisaver_contribution" in data["df"].columns
    assert data["df"]["kiwisaver_contribution"][0] == 1500
    assert data["df"]["kiwisaver_contribution"][1] == 4500


def test_student_loan_rule():
    """Test the StudentLoanRule."""
    rule = StudentLoanRule(
        student_loan_params=StudentLoanParams(
            repayment_threshold=20000, repayment_rate=0.12
        )
    )
    data = {
        "df": pd.DataFrame(
            {
                "familyinc": [50000, 150000],
            }
        )
    }
    rule(data)
    assert "student_loan_repayment" in data["df"].columns
    assert data["df"]["student_loan_repayment"][0] == (50000 - 20000) * 0.12
    assert data["df"]["student_loan_repayment"][1] == (150000 - 20000) * 0.12
