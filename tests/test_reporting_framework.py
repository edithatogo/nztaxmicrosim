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
