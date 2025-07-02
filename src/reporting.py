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
