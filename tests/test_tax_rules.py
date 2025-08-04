"""Tests for the tax rules."""

import pandas as pd

from src.parameters import ACCLevyParams
from src.tax_rules import ACCLevyRule


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
    result = rule(data)
    assert "acc_levy" in data["df"].columns
    assert data["df"]["acc_levy"][0] == 765
    assert data["df"]["acc_levy"][1] == 139111 * 0.0153
