import pandas as pd
from pandas.testing import assert_frame_equal
import numpy as np

from src.reporting import (
    calculate_budget_impact,
    calculate_total_tax_revenue,
    calculate_total_welfare_transfers,
    calculate_net_fiscal_impact,
    calculate_disposable_income,
    calculate_disposable_income_ahc,
    calculate_poverty_rate,
    calculate_child_poverty_rate,
    calculate_gini_coefficient,
    lorenz_curve,
    atkinson_index,
    theil_index,
)


def test_calculate_total_tax_revenue():
    df = pd.DataFrame({"tax_liability": [100, 200, 300]})
    assert calculate_total_tax_revenue(df) == 600


def test_calculate_total_welfare_transfers():
    df = pd.DataFrame(
        {
            "jss_entitlement": [10, 20, 30],
            "sps_entitlement": [5, 10, 15],
            "slp_entitlement": [2, 4, 6],
            "accommodation_supplement_entitlement": [1, 2, 3],
            "wep_entitlement": [0, 0, 0],
            "bstc_entitlement": [0, 0, 0],
            "ftc_entitlement": [0, 0, 0],
            "iwtc_entitlement": [0, 0, 0],
            "mftc_entitlement": [0, 0, 0],
        }
    )
    assert calculate_total_welfare_transfers(df) == 108


def test_calculate_net_fiscal_impact():
    assert calculate_net_fiscal_impact(1000, 200) == 800


def test_calculate_disposable_income():
    df = pd.DataFrame(
        {
            "familyinc": [50000, 60000],
            "tax_liability": [10000, 12000],
            "jss_entitlement": [1000, 0],
            "sps_entitlement": [0, 0],
            "slp_entitlement": [0, 0],
            "accommodation_supplement_entitlement": [0, 0],
            "wep_entitlement": [0, 0],
            "bstc_entitlement": [0, 0],
            "ftc_entitlement": [0, 0],
            "iwtc_entitlement": [0, 0],
            "mftc_entitlement": [0, 0],
        }
    )
    expected = pd.Series([41000, 48000], name="familyinc")
    pd.testing.assert_series_equal(calculate_disposable_income(df), expected)


def test_calculate_disposable_income_ahc():
    df = pd.DataFrame(
        {
            "familyinc": [50000, 60000],
            "tax_liability": [10000, 12000],
            "housing_costs": [15000, 18000],
            "jss_entitlement": [1000, 0],
            "sps_entitlement": [0, 0],
            "slp_entitlement": [0, 0],
            "accommodation_supplement_entitlement": [0, 0],
            "wep_entitlement": [0, 0],
            "bstc_entitlement": [0, 0],
            "ftc_entitlement": [0, 0],
            "iwtc_entitlement": [0, 0],
            "mftc_entitlement": [0, 0],
        }
    )
    expected = pd.Series([26000, 30000])
    pd.testing.assert_series_equal(calculate_disposable_income_ahc(df), expected)


def test_calculate_poverty_rate():
    income_series = pd.Series([10000, 20000, 30000, 40000, 50000])
    poverty_line = 25000
    assert calculate_poverty_rate(income_series, poverty_line) == 40.0


def test_calculate_child_poverty_rate():
    df = pd.DataFrame(
        {
            "age": [10, 25, 15, 40, 5],
            "disposable_income": [15000, 30000, 20000, 50000, 10000],
        }
    )
    poverty_line = 18000
    assert calculate_child_poverty_rate(df, "disposable_income", poverty_line) == (
        2 / 3 * 100
    )


def test_calculate_gini_coefficient():
    income_series = pd.Series([1, 2, 3, 4, 5])
    # Gini for this series is 0.2666...
    assert np.isclose(calculate_gini_coefficient(income_series), 0.26666666666666666)


def test_lorenz_curve():
    income_series = pd.Series([1, 2, 3, 4, 5])
    lorenz = lorenz_curve(income_series)
    assert "population_share" in lorenz.columns
    assert "income_share" in lorenz.columns
    assert np.isclose(lorenz["income_share"].iloc[-1], 1.0)


def test_atkinson_index():
    income_series = pd.Series([1, 2, 3, 4, 5])
    # Atkinson index for this series with epsilon=0.5 is approx 0.069
    assert np.isclose(atkinson_index(income_series), 0.06315339222708627)


def test_theil_index():
    income_series = pd.Series([1, 2, 3, 4, 5])
    # Theil index for this series is approx 0.109
    assert np.isclose(theil_index(income_series), 0.11968759358350925)


def test_calculate_budget_impact():
    baseline = pd.DataFrame(
        {
            "tax_liability": [100, 200],
            "jss_entitlement": [10, 20],
            "sps_entitlement": [0, 0],
            "slp_entitlement": [0, 0],
            "accommodation_supplement_entitlement": [0, 0],
            "wep_entitlement": [0, 0],
            "bstc_entitlement": [0, 0],
            "ftc_entitlement": [0, 0],
            "iwtc_entitlement": [0, 0],
            "mftc_entitlement": [0, 0],
        }
    )
    reform = pd.DataFrame(
        {
            "tax_liability": [120, 230],
            "jss_entitlement": [15, 25],
            "sps_entitlement": [0, 0],
            "slp_entitlement": [0, 0],
            "accommodation_supplement_entitlement": [0, 0],
            "wep_entitlement": [0, 0],
            "bstc_entitlement": [0, 0],
            "ftc_entitlement": [0, 0],
            "iwtc_entitlement": [0, 0],
            "mftc_entitlement": [0, 0],
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

    assert_frame_equal(result.reset_index(drop=True), expected.reset_index(drop=True))