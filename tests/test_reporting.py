from unittest.mock import mock_open, patch

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from src.reporting import (
    atkinson_index,
    calculate_budget_impact,
    calculate_child_poverty_rate,
    calculate_disposable_income,
    calculate_disposable_income_ahc,
    calculate_gini_coefficient,
    calculate_net_fiscal_impact,
    calculate_poverty_rate,
    calculate_total_tax_revenue,
    calculate_total_welfare_transfers,
    generate_microsim_report,
    lorenz_curve,
    plot_evppi,
    plot_evppi_tornado,
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
    assert calculate_child_poverty_rate(df, "disposable_income", poverty_line) == (2 / 3 * 100)


def test_calculate_child_poverty_rate_no_age_column():
    df = pd.DataFrame(
        {
            "disposable_income": [15000, 30000, 20000, 50000, 10000],
        }
    )
    poverty_line = 18000
    assert calculate_child_poverty_rate(df, "disposable_income", poverty_line) == 0.0


def test_calculate_child_poverty_rate_no_children():
    df = pd.DataFrame(
        {
            "age": [20, 25, 35, 40, 50],
            "disposable_income": [15000, 30000, 20000, 50000, 10000],
        }
    )
    poverty_line = 18000
    assert calculate_child_poverty_rate(df, "disposable_income", poverty_line) == 0.0


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





def test_generate_microsim_report():
    """Test the generate_microsim_report function."""
    # Create a dummy DataFrame
    simulated_data = pd.DataFrame(
        {
            "familyinc": [50000],
            "tax_liability": [10000],
            "jss_entitlement": [0],
            "sps_entitlement": [0],
            "slp_entitlement": [0],
            "accommodation_supplement_entitlement": [0],
            "FTCcalc": [0],
            "IWTCcalc": [0],
            "BSTCcalc": [0],
            "MFTCcalc": [0],
            "housing_costs": [0],
            "age": [30],
            "employment_income": [50000],
            "self_employment_income": [0],
            "investment_income": [0],
            "rental_property_income": [0],
            "private_pensions_annuities": [0],
        }
    )
    report_params = {"poverty_line_relative": 0.5}

    # Mock the file writing
    m = mock_open()
    with patch("builtins.open", m):
        with patch("os.path.exists", return_value=True):
            result = generate_microsim_report(simulated_data, report_params)

    # Check that the report was "written"
    m.assert_called_once_with("reports/microsimulation_report.md", "w")

    # Check that the returned dictionary contains the expected components
    expected_keys = [
        "Executive Summary",
        "Fiscal Impact Summary",
        "Distributional Statistics",
        "Equity Metrics",
        "Tax/Benefit Impact by Income Decile",
        "Poverty Rate Changes by Group",
    ]
    assert all(key in result for key in expected_keys)


def test_generate_microsim_report_no_dir():
    """Test the generate_microsim_report function when the reports dir does not exist."""
    # Create a dummy DataFrame
    simulated_data = pd.DataFrame(
        {
            "familyinc": [50000],
            "tax_liability": [10000],
            "jss_entitlement": [0],
            "sps_entitlement": [0],
            "slp_entitlement": [0],
            "accommodation_supplement_entitlement": [0],
            "FTCcalc": [0],
            "IWTCcalc": [0],
            "BSTCcalc": [0],
            "MFTCcalc": [0],
            "housing_costs": [0],
            "age": [30],
            "employment_income": [50000],
            "self_employment_income": [0],
            "investment_income": [0],
            "rental_property_income": [0],
            "private_pensions_annuities": [0],
        }
    )
    report_params = {"poverty_line_relative": 0.5}

    # Mock the file writing
    m = mock_open()
    with patch("builtins.open", m):
        with patch("os.path.exists", return_value=False):
            with patch("os.makedirs") as mock_makedirs:
                result = generate_microsim_report(simulated_data, report_params)

    # Check that the directory was created
    mock_makedirs.assert_called_once_with("reports")

    # Check that the report was "written"
    m.assert_called_once_with("reports/microsimulation_report.md", "w")

    # Check that the returned dictionary contains the expected components
    expected_keys = [
        "Executive Summary",
        "Fiscal Impact Summary",
        "Distributional Statistics",
        "Equity Metrics",
        "Tax/Benefit Impact by Income Decile",
        "Poverty Rate Changes by Group",
    ]
    assert all(key in result for key in expected_keys)





@patch("matplotlib.pyplot.show")
def test_plot_evppi(mock_show):
    """Test the plot_evppi function."""
    evppi_results = {"param1": 0.1, "param2": 0.2}
    plot_evppi(evppi_results)
    mock_show.assert_called_once()


@patch("matplotlib.pyplot.show")
def test_plot_evppi_no_results(mock_show):
    """Test the plot_evppi function with no results."""
    plot_evppi({})
    mock_show.assert_not_called()


@patch("matplotlib.pyplot.savefig")
def test_plot_evppi_save_to_path(mock_savefig):
    """Test the plot_evppi function with an output path."""
    evppi_results = {"param1": 0.1, "param2": 0.2}
    plot_evppi(evppi_results, output_path="test.png")
    mock_savefig.assert_called_once_with("test.png")


@patch("matplotlib.pyplot.show")
def test_plot_evppi_tornado(mock_show):
    """Test the plot_evppi_tornado function."""
    evppi_results = {"param1": 0.1, "param2": 0.2}
    plot_evppi_tornado(evppi_results)
    mock_show.assert_called_once()


@patch("matplotlib.pyplot.show")
def test_plot_evppi_tornado_no_results(mock_show):
    """Test the plot_evppi_tornado function with no results."""
    plot_evppi_tornado({})
    mock_show.assert_not_called()


@patch("matplotlib.pyplot.savefig")
def test_plot_evppi_tornado_save_to_path(mock_savefig):
    """Test the plot_evppi_tornado function with an output path."""
    evppi_results = {"param1": 0.1, "param2": 0.2}
    plot_evppi_tornado(evppi_results, output_path="test.png")
    mock_savefig.assert_called_once_with("test.png")
