import os
from typing import Any, Dict

import pandas as pd

# Import report components from the new framework
from src.reporting_framework import (
    DistributionalStatisticsTable,
    ExecutiveSummary,
    FiscalImpactTable,
    IncomeDecileImpactChart,
    PovertyRateChangesChart,
    ReportGenerator,
)


def calculate_total_tax_revenue(df: pd.DataFrame) -> float:
    """Return the sum of ``tax_liability`` for ``df``."""
    table = FiscalImpactTable()
    return table._calculate_total_tax_revenue(df)


def calculate_total_welfare_transfers(df: pd.DataFrame) -> float:
    """Return the total welfare transfers for ``df``."""
    table = FiscalImpactTable()
    return table._calculate_total_welfare_transfers(df)


def calculate_net_fiscal_impact(tax_revenue: float, welfare_transfers: float) -> float:
    """Return ``tax_revenue`` minus ``welfare_transfers``."""
    table = FiscalImpactTable()
    return table._calculate_net_fiscal_impact(tax_revenue, welfare_transfers)


def calculate_disposable_income(df: pd.DataFrame) -> pd.Series:
    """Calculate disposable income before housing costs."""
    table = DistributionalStatisticsTable()
    return table._calculate_disposable_income(df)


def calculate_disposable_income_ahc(df: pd.DataFrame) -> pd.Series:
    """Calculate disposable income after housing costs."""
    table = DistributionalStatisticsTable()
    return table._calculate_disposable_income_ahc(df)


def calculate_poverty_rate(income_series: pd.Series, poverty_line: float) -> float:
    """Return the share of ``income_series`` below ``poverty_line`` as a percentage."""
    table = DistributionalStatisticsTable()
    return table._calculate_poverty_rate(income_series, poverty_line)


def calculate_child_poverty_rate(df: pd.DataFrame, income_column: str, poverty_line: float) -> float:
    """Return the poverty rate for people under 18."""
    if "age" not in df.columns or income_column not in df.columns:
        return 0.0
    children = df[df["age"] < 18]
    if children.empty:
        return 0.0
    return calculate_poverty_rate(children[income_column], poverty_line)


def calculate_gini_coefficient(income_series: pd.Series) -> float:
    """Return the Gini coefficient for ``income_series``."""
    table = DistributionalStatisticsTable()
    return table._calculate_gini_coefficient(income_series)


def generate_microsim_report(simulated_data: pd.DataFrame, report_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a comprehensive microsimulation report using the defined report components.

    Args:
        simulated_data (pd.DataFrame): The DataFrame containing the simulated population data
                                       with all necessary income, tax, and benefit columns.
        report_params (Dict[str, Any]): A dictionary of parameters for report generation,
                                       e.g., poverty_line_relative.

    Returns:
        Dict[str, Any]: A dictionary where keys are component titles and values are their generated content.
    """
    # Ensure the necessary disposable income columns are present for reporting components
    # These calculations are now handled within the DistributionalStatisticsTable component
    # but ensuring the base data is ready is good practice.

    # Instantiate the desired report components
    components = [
        ExecutiveSummary(),
        FiscalImpactTable(),
        DistributionalStatisticsTable(),
        IncomeDecileImpactChart(),
        PovertyRateChangesChart(),
    ]

    # Create a ReportGenerator instance
    report_generator = ReportGenerator(components)

    # Generate the report content
    generated_content = report_generator.generate_report(simulated_data, report_params)

    # Optionally, compile to a full markdown report and save it
    full_markdown_report = report_generator.to_markdown_report()

    # Ensure the reports directory exists
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)

    report_filepath = os.path.join(reports_dir, "microsimulation_report.md")
    with open(report_filepath, "w") as f:
        f.write(full_markdown_report)
    print(f"Full markdown report saved to {report_filepath}")

    return generated_content


__all__ = [
    "calculate_total_tax_revenue",
    "calculate_total_welfare_transfers",
    "calculate_net_fiscal_impact",
    "calculate_disposable_income",
    "calculate_disposable_income_ahc",
    "calculate_poverty_rate",
    "calculate_child_poverty_rate",
    "calculate_gini_coefficient",
    "generate_microsim_report",
]
