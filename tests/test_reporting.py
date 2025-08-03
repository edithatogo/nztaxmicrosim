import os

import pandas as pd
import pytest

import src.reporting as reporting
from src.reporting import (
    calculate_child_poverty_rate,
    calculate_disposable_income,
)
from src.reporting import calculate_disposable_income_ahc, calculate_gini_coefficient
from src.reporting import calculate_net_fiscal_impact
from src.reporting import calculate_poverty_rate
from src.reporting import calculate_total_tax_revenue
from src.reporting import calculate_total_welfare_transfers
from src.reporting import generate_microsim_report
from src.reporting_framework import (
    EquityMetricsTable,
    calculate_reynolds_smolensky_index,
)
from src.reporting_framework import (
    EquityMetricsTable,
    calculate_reynolds_smolensky_index,
)
from src.reporting_framework import (
    EquityMetricsTable,
    calculate_reynolds_smolensky_index,
)
from src.reporting_framework import (
    EquityMetricsTable,
    calculate_reynolds_smolensky_index,
)
from src.reporting_framework import (
    EquityMetricsTable,
    calculate_reynolds_smolensky_index,
)
from src.reporting_framework import (
    EquityMetricsTable,
    calculate_reynolds_smolensky_index,
)
from src.reporting_framework import (
    EquityMetricsTable,
    calculate_reynolds_smolensky_index,
)


@pytest.fixture
def sample_dataframe():
    # Create a sample DataFrame for testing reporting functions
    data = {
        "employment_income": [50000, 100000, 30000, 0, 20000],
        "self_employment_income": [0, 0, 5000, 0, 0],
        "investment_income": [1000, 5000, 200, 0, 50],
        "rental_property_income": [0, 0, 0, 0, 0],
        "private_pensions_annuities": [0, 0, 0, 15000, 0],
        "tax_liability": [8000, 25000, 3000, 0, 1500],
        "jss_entitlement": [0, 0, 0, 300, 0],  # Weekly amount, will be annualized by calculate_disposable_income
        "sps_entitlement": [0, 0, 0, 0, 0],
        "slp_entitlement": [0, 0, 0, 0, 0],
        "accommodation_supplement_entitlement": [
            0,
            0,
            0,
            100,
            0,
        ],  # Weekly amount, will be annualized by calculate_disposable_income
        "FTCcalc": [5000, 8000, 0, 0, 0],
        "IWTCcalc": [2000, 3000, 0, 0, 0],
        "BSTCcalc": [1000, 0, 0, 0, 0],
        "MFTCcalc": [0, 0, 0, 0, 0],
        "housing_costs": [300, 400, 200, 150, 250],  # Weekly costs
        "age": [35, 40, 28, 68, 10],  # Age for child poverty test
        "num_dependent_children": [2, 2, 0, 0, 0],  # For child poverty test
        "household_size": [4, 4, 1, 1, 1],
    }
    return pd.DataFrame(data)


def test_calculate_total_tax_revenue(sample_dataframe):
    expected_tax_revenue = sample_dataframe["tax_liability"].sum()
    assert calculate_total_tax_revenue(sample_dataframe) == expected_tax_revenue


def test_calculate_total_welfare_transfers(sample_dataframe):
    expected_welfare_transfers = (
        sample_dataframe["jss_entitlement"].sum()
        + sample_dataframe["sps_entitlement"].sum()
        + sample_dataframe["slp_entitlement"].sum()
        + sample_dataframe["accommodation_supplement_entitlement"].sum()
        + sample_dataframe["FTCcalc"].sum()
        + sample_dataframe["IWTCcalc"].sum()
        + sample_dataframe["BSTCcalc"].sum()
        + sample_dataframe["MFTCcalc"].sum()
    )
    assert calculate_total_welfare_transfers(sample_dataframe) == expected_welfare_transfers


def test_calculate_net_fiscal_impact(sample_dataframe):
    tax_revenue = calculate_total_tax_revenue(sample_dataframe)
    welfare_transfers = calculate_total_welfare_transfers(sample_dataframe)
    expected_net_fiscal_impact = tax_revenue - welfare_transfers
    assert calculate_net_fiscal_impact(tax_revenue, welfare_transfers) == expected_net_fiscal_impact


def test_calculate_disposable_income(sample_dataframe):
    df = sample_dataframe.copy()
    df["total_market_income"] = (
        df["employment_income"]
        + df["self_employment_income"]
        + df["investment_income"]
        + df["rental_property_income"]
        + df["private_pensions_annuities"]
    )
    df["total_welfare_transfers_annual"] = (
        df["jss_entitlement"] * 52
        + df["sps_entitlement"] * 52
        + df["slp_entitlement"] * 52
        + df["accommodation_supplement_entitlement"] * 52
        + df["FTCcalc"]
        + df["IWTCcalc"]
        + df["BSTCcalc"]
        + df["MFTCcalc"]
    )
    expected_disposable_income = df["total_market_income"] + df["total_welfare_transfers_annual"] - df["tax_liability"]
    pd.testing.assert_series_equal(calculate_disposable_income(sample_dataframe), expected_disposable_income)


def test_calculate_disposable_income_ahc(sample_dataframe):
    df = sample_dataframe.copy()
    disposable_income = calculate_disposable_income(df)
    expected_disposable_income_ahc = disposable_income - (df["housing_costs"] * 52)
    pd.testing.assert_series_equal(
        calculate_disposable_income_ahc(sample_dataframe),
        expected_disposable_income_ahc,
    )


def test_calculate_poverty_rate(sample_dataframe):
    income_series = pd.Series([10000, 20000, 5000, 30000, 15000])
    poverty_line = 12000
    expected_poverty_rate = (2 / 5) * 100  # 2 incomes (10000, 5000) are below 12000
    assert calculate_poverty_rate(income_series, poverty_line) == expected_poverty_rate

    # Test with empty series
    assert calculate_poverty_rate(pd.Series([]), poverty_line) == 0.0


def test_calculate_child_poverty_rate(sample_dataframe):
    # Assuming 'age' column is present in sample_dataframe
    # Child (age 10) has employment_income 20000, tax_liability 1500, no benefits
    # Disposable income for child: 20000 - 1500 = 18500
    # Let's set a poverty line for children
    poverty_line = 20000
    # Only one child in sample_dataframe (age 10)
    # The child's disposable income is 18500, which is < 20000
    # So, 1 out of 1 child is in poverty
    sample_dataframe["disposable_income"] = calculate_disposable_income(sample_dataframe)
    sample_dataframe["disposable_income_ahc"] = calculate_disposable_income_ahc(sample_dataframe)

    # Test BHC child poverty
    # Child's BHC income: 20000 (employment) - 1500 (tax) = 18500
    # Poverty line: 20000
    # Expected: 100% (1 child out of 1 is below poverty line)
    assert calculate_child_poverty_rate(sample_dataframe, "disposable_income", poverty_line) == 100.0

    # Test AHC child poverty
    # Child's AHC income: 18500 (BHC) - (250 * 52) (housing) = 18500 - 13000 = 5500
    # Poverty line: 20000
    # Expected: 100% (1 child out of 1 is below poverty line)
    assert calculate_child_poverty_rate(sample_dataframe, "disposable_income_ahc", poverty_line) == 100.0

    # Test with no children in dataframe
    df_no_children = sample_dataframe[sample_dataframe["age"] >= 18]
    assert calculate_child_poverty_rate(df_no_children, "disposable_income", poverty_line) == 0.0


def test_calculate_gini_coefficient(sample_dataframe):
    income_series = pd.Series([10000, 20000, 5000, 30000, 15000])
    # Expected Gini for this series (calculated manually or using a known library)
    # Using a quick online calculator for [5000, 10000, 15000, 20000, 30000] gives ~0.28
    # Due to floating point precision, we'll use pytest.approx
    expected_gini = 0.30
    assert calculate_gini_coefficient(income_series) == pytest.approx(expected_gini, abs=0.01)

    # Test with all equal incomes (Gini should be 0)
    assert calculate_gini_coefficient(pd.Series([100, 100, 100])) == 0.0

    # Test with empty series
    assert calculate_gini_coefficient(pd.Series([])) == 0.0

    # Test with single value series
    assert calculate_gini_coefficient(pd.Series([100])) == 0.0


def test_generate_microsim_report_expected_keys(sample_dataframe, tmp_path, monkeypatch):
    df = sample_dataframe.copy()
    df["disposable_income"] = calculate_disposable_income(df)

    # Change working directory so report files are written to a temporary location
    monkeypatch.chdir(tmp_path)
    result = generate_microsim_report(df, {"poverty_line_relative": 0.5})

    assert "Executive Summary" in result
    assert "Fiscal Impact Summary" in result


def test_lorenz_and_inequality_indices():
    incomes = pd.Series([-1, 1, 2, 3, 4])

    # Lorenz curve should start at (0,0) and end at (1,1)
    lorenz = reporting.lorenz_curve(incomes)
    expected = pd.DataFrame(
        {
            "population_share": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
            "income_share": [0.0, 0.0, 0.1, 0.3, 0.6, 1.0],
        }
    )
    pd.testing.assert_frame_equal(lorenz.reset_index(drop=True), expected)

    # Atkinson and Theil indices for this distribution
    assert reporting.atkinson_index(incomes, epsilon=0.5) == pytest.approx(0.0556, abs=1e-3)
    assert reporting.theil_index(incomes) == pytest.approx(0.1064, abs=1e-3)


def test_inequality_edge_cases():
    incomes_equal = pd.Series([10, 10, 10])
    assert reporting.atkinson_index(incomes_equal) == pytest.approx(0.0, abs=1e-12)
    assert reporting.theil_index(incomes_equal) == pytest.approx(0.0, abs=1e-12)

    incomes_empty = pd.Series([], dtype=float)
    lorenz = reporting.lorenz_curve(incomes_empty)
    assert lorenz.equals(pd.DataFrame({"population_share": [0.0], "income_share": [0.0]}))


def test_plot_evppi(tmp_path):
    """Test that plot_evppi creates an output file."""
    evppi_results = {"param1": 0.5, "param2": 1.2, "param3": 0.8}
    output_file = tmp_path / "evppi_plot.png"

    reporting.plot_evppi(
        evppi_results,
        output_path=str(output_file),
        palette="coolwarm",
        xlabel="Custom X Label",
        ylabel="Custom Y Label",
    )

    assert os.path.exists(output_file)


def test_plot_evppi_no_data():
    """Test that plot_evppi handles empty data without crashing."""
    # This test just checks that the function runs without error
    reporting.plot_evppi({})


def test_calculate_reynolds_smolensky_index(sample_dataframe):
    """Test the Reynolds-Smolensky index calculation."""
    market_income = (
        sample_dataframe["employment_income"]
        + sample_dataframe["self_employment_income"]
        + sample_dataframe["investment_income"]
        + sample_dataframe["rental_property_income"]
        + sample_dataframe["private_pensions_annuities"]
    )
    disposable_income = calculate_disposable_income(sample_dataframe)

    # Gini of market income - Gini of disposable income
    # Gini of market income - Gini of disposable income
    gini_market = calculate_gini_coefficient(market_income)
    gini_disposable = calculate_gini_coefficient(disposable_income)
    expected_rs = gini_market - gini_disposable

    rs_index = calculate_reynolds_smolensky_index(market_income, disposable_income)
    assert rs_index == pytest.approx(expected_rs)


def test_equity_metrics_table(sample_dataframe):
    """Test the EquityMetricsTable component."""
    equity_table = EquityMetricsTable()
    result = equity_table.generate(sample_dataframe, {})

    assert isinstance(result, pd.DataFrame)
    assert "Metric" in result.columns
    assert "Value" in result.columns
    assert len(result) == 4
    assert "Reynolds-Smolensky Index" in result["Metric"].values


def test_plot_evppi_tornado(tmp_path):
    """Test that plot_evppi_tornado creates an output file."""
    evppi_results = {"param1": 0.5, "param2": 1.2, "param3": 0.8}
    output_file = tmp_path / "evppi_tornado_plot.png"

    reporting.plot_evppi_tornado(
        evppi_results,
        output_path=str(output_file),
        color="red",
        xlabel="Custom X Label",
    )

    assert os.path.exists(output_file)


def test_plot_evppi_tornado_no_data():
    """Test that plot_evppi_tornado handles empty data without crashing."""
    # This test just checks that the function runs without error
    reporting.plot_evppi_tornado({})


def test_atkinson_epsilon_one():
    incomes = pd.Series([1, 2, 3, 4])
    assert reporting.atkinson_index(incomes, epsilon=1) == pytest.approx(0.1147, abs=1e-3)
