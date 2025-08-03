import os
from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Import report components from the new framework
from src.reporting_framework import (
    DistributionalStatisticsTable,
    ExecutiveSummary,
    FiscalImpactTable,
    IncomeDecileImpactChart,
    PovertyRateChangesChart,
    ReportGenerator,
    calculate_atkinson_index,
    calculate_lorenz_curve,
    calculate_theil_index,
)

# Instantiate helpers used by the backward compatible wrapper functions.
_fiscal_helper = FiscalImpactTable()
_stats_helper = DistributionalStatisticsTable()


def calculate_total_tax_revenue(df: pd.DataFrame) -> float:
    """Return the sum of ``tax_liability`` for ``df``."""
    return _fiscal_helper._calculate_total_tax_revenue(df)


def calculate_total_welfare_transfers(df: pd.DataFrame) -> float:
    """Return the total welfare transfers for ``df``."""
    return _fiscal_helper._calculate_total_welfare_transfers(df)


def calculate_net_fiscal_impact(tax_revenue: float, welfare_transfers: float) -> float:
    """Return ``tax_revenue`` minus ``welfare_transfers``."""
    return _fiscal_helper._calculate_net_fiscal_impact(tax_revenue, welfare_transfers)


def calculate_disposable_income(df: pd.DataFrame) -> pd.Series:
    """Calculate disposable income before housing costs."""
    return _stats_helper._calculate_disposable_income(df)


def calculate_disposable_income_ahc(df: pd.DataFrame) -> pd.Series:
    """Calculate disposable income after housing costs."""
    return _stats_helper._calculate_disposable_income_ahc(df)


def calculate_poverty_rate(income_series: pd.Series, poverty_line: float) -> float:
    """Return the share of ``income_series`` below ``poverty_line`` as a percentage."""
    return _stats_helper._calculate_poverty_rate(income_series, poverty_line)


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
    return _stats_helper._calculate_gini_coefficient(income_series)


def lorenz_curve(income_series: pd.Series) -> pd.DataFrame:
    """Return the Lorenz curve for ``income_series``.

    The returned DataFrame contains the cumulative population and income shares
    starting from the lowest income.
    """
    return calculate_lorenz_curve(income_series)


def atkinson_index(income_series: pd.Series, epsilon: float = 0.5) -> float:
    """Return the Atkinson inequality index for ``income_series``.

    ``epsilon`` controls inequality aversion: larger values give more weight to
    lower incomes.
    """
    return calculate_atkinson_index(income_series, epsilon)


def theil_index(income_series: pd.Series) -> float:
    """Return the Theil T index for ``income_series``."""
    return calculate_theil_index(income_series)


def calculate_budget_impact(baseline_df: pd.DataFrame, reform_df: pd.DataFrame) -> pd.DataFrame:
    """Return fiscal metrics for baseline and reform scenarios and their difference."""
    baseline_tax = calculate_total_tax_revenue(baseline_df)
    baseline_welfare = calculate_total_welfare_transfers(baseline_df)
    baseline_net = calculate_net_fiscal_impact(baseline_tax, baseline_welfare)

    reform_tax = calculate_total_tax_revenue(reform_df)
    reform_welfare = calculate_total_welfare_transfers(reform_df)
    reform_net = calculate_net_fiscal_impact(reform_tax, reform_welfare)

    data = {
        "Metric": [
            "Total Tax Revenue",
            "Total Welfare Transfers",
            "Net Fiscal Impact",
        ],
        "Baseline": [baseline_tax, baseline_welfare, baseline_net],
        "Reform": [reform_tax, reform_welfare, reform_net],
    }
    df = pd.DataFrame(data)
    df["Difference"] = df["Reform"] - df["Baseline"]
    return df


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
def plot_evppi(
    evppi_results: Dict[str, float],
    title: str = "Expected Value of Perfect Partial Information",
    output_path: str = None,
):
    """
    Generates a bar chart of EVPPI results.

    Args:
        evppi_results (Dict[str, float]): A dictionary where keys are parameter
                                          names and values are their EVPPI.
        title (str, optional): The title of the plot. Defaults to "Expected Value of Perfect Partial Information".
        output_path (str, optional): The path to save the plot to. If None, the plot is shown. Defaults to None.
    """
    if not evppi_results:
        print("No EVPPI results to plot.")
        return

    # Sort by value for better visualization
    sorted_evppi = sorted(evppi_results.items(), key=lambda item: item[1], reverse=True)
    params, values = zip(*sorted_evppi)

    plt.figure(figsize=(10, 6))
    sns.barplot(x=list(values), y=list(params), palette="viridis")
    plt.xlabel("EVPPI")
    plt.ylabel("Parameters")
    plt.title(title)
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path)
        print(f"Plot saved to {output_path}")
    else:
        plt.show()


# ---------------------------------------------------------------------------
# Helper functions for unit tests
__all__ = [
    "plot_evppi",
    "calculate_total_tax_revenue",
    "calculate_total_welfare_transfers",
    "calculate_net_fiscal_impact",
    "calculate_disposable_income",
    "calculate_disposable_income_ahc",
    "calculate_poverty_rate",
    "calculate_child_poverty_rate",
    "calculate_gini_coefficient",
    "lorenz_curve",
    "atkinson_index",
    "theil_index",
    "calculate_budget_impact",
    "generate_microsim_report",
]
