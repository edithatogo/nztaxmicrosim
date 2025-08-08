import os
import runpy
from typing import Any
from unittest.mock import MagicMock, patch

import matplotlib.pyplot as plt
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
    df = pd.DataFrame(data)
    df["disposable_income"] = DistributionalStatisticsTable()._calculate_disposable_income(df)
    df["disposable_income_ahc"] = DistributionalStatisticsTable()._calculate_disposable_income_ahc(df)
    return df


def test_main_block(capsys):
    """Test the main execution block."""
    runpy.run_module("src.reporting_framework", run_name="__main__")
    captured = capsys.readouterr()
    assert "Executive Summary" in captured.out
    assert "Fiscal Impact Summary" in captured.out
    assert "Distributional Statistics" in captured.out
    assert "Tax/Benefit Impact by Income Decile" in captured.out
    assert "Poverty Rate Changes by Group" in captured.out


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
