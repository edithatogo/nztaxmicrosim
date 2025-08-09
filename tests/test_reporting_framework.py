import os
import runpy
from typing import Any
from unittest.mock import MagicMock, patch

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

from src.reporting_framework import (
    DistributionalStatisticsTable,
    EquityMetricsTable,
    ExecutiveSummary,
    FiscalImpactTable,
    IncomeDecileImpactChart,
    PovertyRateChangesChart,
    ReportComponent,
    ReportGenerator,
)


@pytest.fixture
def sample_dataframe():
    # Create a sample DataFrame for testing reporting functions
    data = {
        "familyinc": [51000, 105000, 35200, 15000, 20050],
        "tax_liability": [8000, 25000, 3000, 0, 1500],
        "jss_entitlement": [0, 0, 0, 300, 0],
        "sps_entitlement": [0, 0, 0, 0, 0],
        "slp_entitlement": [0, 0, 0, 0, 0],
        "accommodation_supplement_entitlement": [
            0,
            0,
            0,
            100,
            0,
        ],
        "FTCcalc": [5000, 8000, 0, 0, 0],
        "IWTCcalc": [2000, 3000, 0, 0, 0],
        "BSTCcalc": [1000, 0, 0, 0, 0],
        "MFTCcalc": [0, 0, 0, 0, 0],
        "housing_costs": [300, 400, 200, 150, 250],
        "age": [35, 40, 28, 68, 10],
        "num_dependent_children": [2, 2, 0, 0, 0],
        "household_size": [4, 4, 1, 1, 1],
    }
    df = pd.DataFrame(data)
    df["disposable_income"] = DistributionalStatisticsTable()._calculate_disposable_income(df)
    df["disposable_income_ahc"] = DistributionalStatisticsTable()._calculate_disposable_income_ahc(df)
    return df


def test_main_block():
    """Test the main execution block."""
    # Instantiate report components
    components = [
        ExecutiveSummary(),
        FiscalImpactTable(),
        DistributionalStatisticsTable(),
        IncomeDecileImpactChart(),
        PovertyRateChangesChart(),
    ]

    # Create a ReportGenerator instance
    report_gen = ReportGenerator(components)

    # Define global parameters for the report
    global_report_params = {
        "poverty_line_relative": 0.6  # Example: 60% of median income for poverty line
    }

    # Generate the report
    # Create dummy data for demonstration
    import numpy as np
    np.random.seed(42)
    num_people = 1000
    dummy_data = pd.DataFrame(
        {
            "employment_income": np.random.normal(50000, 15000, num_people),
            "self_employment_income": np.random.normal(5000, 2000, num_people),
            "investment_income": np.random.normal(1000, 500, num_people),
            "rental_property_income": np.random.normal(2000, 1000, num_people),
            "private_pensions_annuities": np.random.normal(3000, 1000, num_people),
            "tax_liability": np.random.normal(8000, 3000, num_people).clip(min=0),
            "jss_entitlement": np.random.normal(100, 50, num_people).clip(min=0),  # weekly
            "sps_entitlement": np.random.normal(50, 20, num_people).clip(min=0),  # weekly
            "slp_entitlement": np.random.normal(30, 10, num_people).clip(min=0),  # weekly
            "accommodation_supplement_entitlement": np.random.normal(20, 10, num_people).clip(min=0),  # weekly
            "FTCcalc": np.random.normal(1000, 300, num_people).clip(min=0),  # annual
            "IWTCcalc": np.random.normal(500, 200, num_people).clip(min=0),  # annual
            "BSTCcalc": np.random.normal(200, 100, num_people).clip(min=0),  # annual
            "MFTCcalc": np.random.normal(150, 50, num_people).clip(min=0),  # annual
            "housing_costs": np.random.normal(200, 50, num_people).clip(min=0),  # weekly
            "age": np.random.randint(0, 90, num_people),
            "familyinc": np.random.normal(50000, 15000, num_people),
        }
    )
    
    # Calculate disposable income and AHC for dummy data
    # These functions would ideally come from src/reporting.py or a shared utility
    def calculate_disposable_income_dummy(df: pd.DataFrame) -> pd.Series:
        disposable_income = (
            df["employment_income"]
            + df["self_employment_income"]
            + df["investment_income"]
            + df["rental_property_income"]
            + df["private_pensions_annuities"]
        )
        for col in ["jss_entitlement", "sps_entitlement", "slp_entitlement", "accommodation_supplement_entitlement"]:
            disposable_income += df[col] * 52
        for col in ["FTCcalc", "IWTCcalc", "BSTCcalc", "MFTCcalc"]:
            disposable_income += df[col]
        disposable_income -= df["tax_liability"]
        return disposable_income

    def calculate_disposable_income_ahc_dummy(df: pd.DataFrame) -> pd.Series:
        disposable_income = calculate_disposable_income_dummy(df)
        return disposable_income - (df["housing_costs"] * 52)

    dummy_data["disposable_income"] = calculate_disposable_income_dummy(dummy_data)
    dummy_data["disposable_income_ahc"] = calculate_disposable_income_ahc_dummy(dummy_data)
    
    generated_report_content = report_gen.generate_report(dummy_data, global_report_params)

    # Compile to Markdown
    full_markdown_report = report_gen.to_markdown_report()

    assert "Executive Summary" in full_markdown_report
    assert "Fiscal Impact Summary" in full_markdown_report
    assert "Distributional Statistics" in full_markdown_report
    assert "Tax/Benefit Impact by Income Decile" in full_markdown_report
    assert "Poverty Rate Changes by Group" in full_markdown_report


def test_report_generator_error_handling():
    """Test that the ReportGenerator handles errors in components gracefully."""

    class FailingComponent(ReportComponent):
        def __init__(self):
            super().__init__("Failing Component", "This component always fails.")

        def generate(self, data: pd.DataFrame, params: dict) -> Any:
            raise ValueError("This is a test error.")

    components = [ExecutiveSummary(), FailingComponent()]
    report_gen = ReportGenerator(components)
    report_gen.generate_report(pd.DataFrame(), {})

    assert "Executive Summary" in report_gen.generated_content
    assert "Failing Component" in report_gen.generated_content
    assert isinstance(report_gen.generated_content["Failing Component"], str)
    assert "Error: This is a test error." in report_gen.generated_content["Failing Component"]

    markdown = report_gen.to_markdown_report()
    assert "## Failing Component" in markdown
    assert "Error: This is a test error." in markdown


def test_report_component_generate():
    """Test that the base ReportComponent.generate method raises NotImplementedError."""
    component = ReportComponent("Test", "Test")
    with pytest.raises(NotImplementedError):
        component.generate(pd.DataFrame(), {})


def test_fiscal_impact_table_no_tax_liability():
    """Test the FiscalImpactTable when 'tax_liability' is missing."""
    table = FiscalImpactTable()
    df = pd.DataFrame({'jss_entitlement': [10]})
    result = table.generate(df, {})
    assert result['Value'][0] == 0.0


def test_distributional_statistics_table_poverty_rate_empty():
    """Test the _calculate_poverty_rate method with an empty series."""
    table = DistributionalStatisticsTable()
    assert table._calculate_poverty_rate(pd.Series([], dtype=float), 1000) == 0.0


def test_income_decile_impact_chart_error_handling(sample_dataframe):
    """Test that the IncomeDecileImpactChart handles missing columns."""
    chart = IncomeDecileImpactChart()
    df = sample_dataframe.drop(columns=["disposable_income"])
    with pytest.raises(ValueError, match="DataFrame must contain 'disposable_income' column."):
        chart.generate(df, {})


def test_poverty_rate_changes_chart_error_handling(sample_dataframe):
    """Test that the PovertyRateChangesChart handles missing columns."""
    chart = PovertyRateChangesChart()
    df = sample_dataframe.drop(columns=["disposable_income"])
    with pytest.raises(ValueError, match="DataFrame must contain 'disposable_income' and 'age' columns."):
        chart.generate(df, {})


from src.reporting_framework import calculate_lorenz_curve, calculate_atkinson_index, calculate_theil_index

def test_calculate_lorenz_curve_zero_income():
    """Test the Lorenz curve calculation with zero total income."""
    income_series = pd.Series([0, 0, 0, 0, 0])
    lorenz = calculate_lorenz_curve(income_series)
    assert "population_share" in lorenz.columns
    assert "income_share" in lorenz.columns
    assert lorenz["income_share"].iloc[-1] == 0.0

def test_calculate_lorenz_curve_empty_series():
    """Test the Lorenz curve calculation with an empty series."""
    income_series = pd.Series([], dtype=float)
    lorenz = calculate_lorenz_curve(income_series)
    assert "population_share" in lorenz.columns
    assert "income_share" in lorenz.columns
    assert lorenz.to_dict() == {'population_share': {0: 0.0}, 'income_share': {0: 0.0}}

def test_calculate_atkinson_index_empty_series():
    """Test the Atkinson index calculation with an empty series."""
    income_series = pd.Series([], dtype=float)
    assert calculate_atkinson_index(income_series) == 0.0

def test_calculate_theil_index_empty_series():
    """Test the Theil index calculation with an empty series."""
    income_series = pd.Series([], dtype=float)
    assert calculate_theil_index(income_series) == 0.0


def test_calculate_atkinson_index_epsilon_one():
    """Test the Atkinson index calculation with epsilon = 1."""
    income_series = pd.Series([1, 2, 3, 4, 5])
    # The geometric mean is approx 2.605
    # The arithmetic mean is 3.0
    # The expected index is 1 - (2.605 / 3.0) = 0.1316
    assert np.isclose(calculate_atkinson_index(income_series, epsilon=1), 0.13160963843421614)

def test_distributional_statistics_table_empty_input():
    """Test the DistributionalStatisticsTable with an empty DataFrame."""
    table = DistributionalStatisticsTable()
    df = pd.DataFrame({
        "familyinc": [],
        "tax_liability": [],
        "jss_entitlement": [],
        "sps_entitlement": [],
        "slp_entitlement": [],
        "accommodation_supplement_entitlement": [],
        "FTCcalc": [],
        "IWTCcalc": [],
        "BSTCcalc": [],
        "MFTCcalc": [],
        "housing_costs": [],
    })
    # Expect the generate method to handle empty input gracefully
    result = table.generate(df, {})
    assert isinstance(result, pd.DataFrame)
    assert not result.empty

def test_income_decile_impact_chart_to_markdown():
    """Test the to_markdown method of IncomeDecileImpactChart."""
    chart = IncomeDecileImpactChart()
    # Test with a figure
    fig, ax = plt.subplots()
    markdown = chart.to_markdown(fig)
    assert "![Tax/Benefit Impact by Income Decile](reports/tax/benefit_impact_by_income_decile.png)" in markdown
    # Test with an error message
    markdown = chart.to_markdown("Error: Test error")
    assert "Error: Test error" in markdown

def test_report_generator_to_markdown_fallback():
    """Test the fallback case in ReportGenerator.to_markdown_report."""
    class SimpleComponent(ReportComponent):
        def generate(self, data: pd.DataFrame, params: dict) -> Any:
            return "Simple content"
    
    components = [SimpleComponent("Simple Component", "A simple component.")]
    report_gen = ReportGenerator(components)
    report_gen.generate_report(pd.DataFrame(), {})
    markdown = report_gen.to_markdown_report()
    assert "## Simple Component" in markdown
    assert "Simple content" in markdown


def test_distributional_statistics_table_to_markdown_string_input():
    """Test the to_markdown method of DistributionalStatisticsTable with a string input."""
    table = DistributionalStatisticsTable()
    markdown = table.to_markdown("Test content")
    assert "Test content" in markdown


def test_main_script_execution():
    """Test the main execution block of the script."""
    with patch('builtins.print') as mock_print:
        runpy.run_path('src/reporting_framework.py', run_name='__main__')
        # Check that the final print statement is called
        mock_print.assert_called_with("Dummy report components generated and saved to 'reports/' directory.")
