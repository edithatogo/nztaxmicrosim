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


# ---------------------------------------------------------------------------
# Helper functions for unit tests
# ---------------------------------------------------------------------------


def calculate_total_tax_revenue(df: pd.DataFrame) -> float:
    """Return the total tax liability from the dataframe."""
    if "tax_liability" not in df.columns:
        return 0.0
    return float(df["tax_liability"].sum())


def calculate_total_welfare_transfers(df: pd.DataFrame) -> float:
    """Return the sum of all welfare transfer columns."""
    total = 0.0
    for col in [
        "jss_entitlement",
        "sps_entitlement",
        "slp_entitlement",
        "accommodation_supplement_entitlement",
        "FTCcalc",
        "IWTCcalc",
        "BSTCcalc",
        "MFTCcalc",
    ]:
        if col in df.columns:
            total += df[col].sum()
    return float(total)


def calculate_net_fiscal_impact(tax_revenue: float, welfare_transfers: float) -> float:
    """Return the net fiscal impact (tax revenue minus welfare transfers)."""
    return float(tax_revenue - welfare_transfers)


def calculate_disposable_income(df: pd.DataFrame) -> pd.Series:
    """Calculate disposable income before housing costs."""
    disposable_income = (
        df["employment_income"]
        + df["self_employment_income"]
        + df["investment_income"]
        + df["rental_property_income"]
        + df["private_pensions_annuities"]
    )
    for col in [
        "jss_entitlement",
        "sps_entitlement",
        "slp_entitlement",
        "accommodation_supplement_entitlement",
    ]:
        if col in df.columns:
            disposable_income += df[col] * 52
    for col in ["FTCcalc", "IWTCcalc", "BSTCcalc", "MFTCcalc"]:
        if col in df.columns:
            disposable_income += df[col]
    if "tax_liability" in df.columns:
        disposable_income -= df["tax_liability"]
    return disposable_income


def calculate_disposable_income_ahc(df: pd.DataFrame) -> pd.Series:
    """Calculate disposable income after housing costs."""
    disposable_income = calculate_disposable_income(df)
    if "housing_costs" in df.columns:
        disposable_income -= df["housing_costs"] * 52
    return disposable_income


def calculate_poverty_rate(income_series: pd.Series, poverty_line: float) -> float:
    """Calculate the share of individuals below the poverty line."""
    if income_series.empty:
        return 0.0
    return float((income_series < poverty_line).sum() / len(income_series) * 100)


def calculate_child_poverty_rate(df: pd.DataFrame, income_column: str, poverty_line: float) -> float:
    """Calculate poverty rate among children (<18)."""
    if "age" not in df.columns or income_column not in df.columns:
        return 0.0
    children = df[df["age"] < 18]
    if children.empty:
        return 0.0
    return float((children[income_column] < poverty_line).sum() / len(children) * 100)


def calculate_gini_coefficient(income_series: pd.Series) -> float:
    """Calculate the Gini coefficient for a series of incomes."""
    if income_series.empty or len(income_series) == 1:
        return 0.0
    sorted_income = income_series.sort_values().values
    n = len(sorted_income)
    numerator = (2 * (pd.Series(range(1, n + 1)))).sub(n + 1).mul(sorted_income).sum()
    denominator = n * sorted_income.sum()
    return float(numerator / denominator) if denominator != 0 else 0.0
