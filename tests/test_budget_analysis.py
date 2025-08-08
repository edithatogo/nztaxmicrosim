import pandas as pd
from pandas.testing import assert_frame_equal

from src.reporting import calculate_budget_impact


def test_calculate_budget_impact():
    baseline = pd.DataFrame(
        {
            "tax_liability": [100, 200],
            "jss_entitlement": [10, 20],
        }
    )
    reform = pd.DataFrame(
        {
            "tax_liability": [120, 230],
            "jss_entitlement": [15, 25],
        }
    )

    result = calculate_budget_impact(baseline, reform)

    baseline_tax = 300.0
    baseline_welfare = 30.0
    baseline_net = baseline_tax - baseline_welfare

    reform_tax = 350.0
    reform_welfare = 40.0
    reform_net = reform_tax - reform_welfare

    expected = pd.DataFrame(
        {
            "Metric": [
                "Total Tax Revenue",
                "Total Welfare Transfers",
                "Net Fiscal Impact",
            ],
            "Baseline": [baseline_tax, baseline_welfare, baseline_net],
            "Reform": [reform_tax, reform_welfare, reform_net],
        }
    )
    expected["Difference"] = expected["Reform"] - expected["Baseline"]

    assert_frame_equal(result.reset_index(drop=True), expected)
