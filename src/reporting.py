import os
from typing import Any, Dict, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Import report components from the new framework
from src.reporting_framework import (
    DistributionalStatisticsTable,
    EquityMetricsTable,
    ExecutiveSummary,
    FiscalImpactTable,
    IncomeDecileImpactChart,
    PovertyRateChangesChart,
    ReportGenerator,
    calculate_atkinson_index,
    calculate_lorenz_curve,
    calculate_reynolds_smolensky_index,
    calculate_theil_index,
)

# Instantiate helpers used by the backward compatible wrapper functions.
_fiscal_helper = FiscalImpactTable()
_stats_helper = DistributionalStatisticsTable()


def calculate_total_tax_revenue(df: pd.DataFrame) -> float:
    """Calculate the total tax revenue from a DataFrame.

    This function sums the 'tax_liability' column of the given DataFrame.

    Args:
        df: A pandas DataFrame with a 'tax_liability' column.

    Returns:
        The total tax revenue.
    """
    return _fiscal_helper._calculate_total_tax_revenue(df)


def calculate_total_welfare_transfers(df: pd.DataFrame) -> float:
    """Calculate the total welfare transfers from a DataFrame.

    This function sums the entitlement columns for various benefits and
    tax credits in the given DataFrame.

    Args:
        df: A pandas DataFrame with entitlement columns (e.g.,
            'jss_entitlement', 'ftc_entitlement').

    Returns:
        The total welfare transfers.
    """
    return _fiscal_helper._calculate_total_welfare_transfers(df)


def calculate_net_fiscal_impact(tax_revenue: float, welfare_transfers: float) -> float:
    """Calculate the net fiscal impact.

    This is the difference between total tax revenue and total welfare
    transfers.

    Args:
        tax_revenue: The total tax revenue.
        welfare_transfers: The total welfare transfers.

    Returns:
        The net fiscal impact.
    """
    return _fiscal_helper._calculate_net_fiscal_impact(tax_revenue, welfare_transfers)


def calculate_disposable_income(df: pd.DataFrame) -> pd.Series:
    """Calculate disposable income before housing costs.

    Disposable income is calculated as family income plus benefits and
    tax credits, minus tax liability.

    Args:
        df: A pandas DataFrame with income, benefit, and tax columns.

    Returns:
        A pandas Series containing the disposable income for each row.
    """
    return _stats_helper._calculate_disposable_income(df)


def calculate_disposable_income_ahc(df: pd.DataFrame) -> pd.Series:
    """Calculate disposable income after housing costs.

    This is disposable income minus housing costs.

    Args:
        df: A pandas DataFrame with disposable income and 'housing_costs'
            columns.

    Returns:
        A pandas Series containing the after-housing-cost disposable
        income for each row.
    """
    return _stats_helper._calculate_disposable_income_ahc(df)


def calculate_poverty_rate(income_series: pd.Series, poverty_line: float) -> float:
    """Calculate the poverty rate for a given income series.

    The poverty rate is the percentage of individuals with income below the
    poverty line.

    Args:
        income_series: A pandas Series of income values.
        poverty_line: The poverty line.

    Returns:
        The poverty rate as a percentage.
    """
    return _stats_helper._calculate_poverty_rate(income_series, poverty_line)


def calculate_child_poverty_rate(df: pd.DataFrame, income_column: str, poverty_line: float) -> float:
    """Calculate the poverty rate for children (under 18).

    Args:
        df: A pandas DataFrame with 'age' and income columns.
        income_column: The name of the income column to use.
        poverty_line: The poverty line.

    Returns:
        The child poverty rate as a percentage.
    """
    if "age" not in df.columns or income_column not in df.columns:
        return 0.0
    children = df[df["age"] < 18]
    if children.empty:
        return 0.0
    return calculate_poverty_rate(children[income_column], poverty_line)


def calculate_gini_coefficient(income_series: pd.Series) -> float:
    """Calculate the Gini coefficient for a given income series.

    The Gini coefficient is a measure of statistical dispersion intended to
    represent the income or wealth distribution of a nation's residents,
    and is the most commonly used measure of inequality.

    Args:
        income_series: A pandas Series of income values.

    Returns:
        The Gini coefficient.
    """
    return _stats_helper._calculate_gini_coefficient(income_series)


def lorenz_curve(income_series: pd.Series) -> pd.DataFrame:
    """Calculate the Lorenz curve for a given income series.

    The Lorenz curve is a graphical representation of the distribution of
    income or of wealth.

    Args:
        income_series: A pandas Series of income values.

    Returns:
        A DataFrame with 'population_share' and 'income_share' columns,
        representing the points on the Lorenz curve.
    """
    return calculate_lorenz_curve(income_series)


def atkinson_index(income_series: pd.Series, epsilon: float = 0.5) -> float:
    """Calculate the Atkinson index for a given income series.

    The Atkinson index is a measure of income inequality.

    Args:
        income_series: A pandas Series of income values.
        epsilon: The inequality aversion parameter. A higher value means
            more weight is given to inequalities at the lower end of the
            distribution.

    Returns:
        The Atkinson index.
    """
    return calculate_atkinson_index(income_series, epsilon)


def theil_index(income_series: pd.Series) -> float:
    """Calculate the Theil T index for a given income series.

    The Theil index is a measure of economic inequality.

    Args:
        income_series: A pandas Series of income values.

    Returns:
        The Theil T index.
    """
    return calculate_theil_index(income_series)


def calculate_budget_impact(baseline_df: pd.DataFrame, reform_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate the fiscal impact of a reform.

    This function compares the fiscal metrics of a baseline scenario and a
    reform scenario, and returns a DataFrame summarizing the differences.

    Args:
        baseline_df: A DataFrame representing the baseline scenario.
        reform_df: A DataFrame representing the reform scenario.

    Returns:
        A DataFrame with the fiscal metrics for both scenarios and their
        difference.
    """
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
    Generate a comprehensive microsimulation report.

    This function orchestrates the generation of a multi-component report
    from simulated microsimulation data. It uses a `ReportGenerator` to
    create various components like an executive summary, fiscal impact tables,
    and distributional statistics.

    The generated report is also saved as a markdown file.

    Args:
        simulated_data: A DataFrame containing the simulated population data,
            including income, tax, and benefit columns.
        report_params: A dictionary of parameters for report generation,
            such as the poverty line definition.

    Returns:
        A dictionary where keys are the titles of the report components and
        values are their generated content (e.g., DataFrames, plots).
    """
    # Ensure the necessary disposable income columns are present for reporting components
    # These calculations are now handled within the DistributionalStatisticsTable component
    # but ensuring the base data is ready is good practice.

    # Instantiate the desired report components
    components = [
        ExecutiveSummary(),
        FiscalImpactTable(),
        DistributionalStatisticsTable(),
        EquityMetricsTable(),
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
    output_path: Union[str, None] = None,
    palette: str = "viridis",
    xlabel: str = "EVPPI",
    ylabel: str = "Parameters",
):
    """
    Generate a bar chart of EVPPI results.

    The Expected Value of Perfect Partial Information (EVPPI) is a measure
    of the expected value of learning the true value of a subset of uncertain
    parameters. This plot helps to identify which parameters have the most
    influence on the model's output.

    Args:
        evppi_results: A dictionary where keys are parameter names and
            values are their EVPPI.
        title: The title of the plot.
        output_path: The path to save the plot to. If None, the plot is
            displayed directly.
        palette: The color palette to use for the plot.
        xlabel: The label for the x-axis.
        ylabel: The label for the y-axis.
    """
    if not evppi_results:
        print("No EVPPI results to plot.")
        return

    # Sort by value for better visualization
    sorted_evppi = sorted(evppi_results.items(), key=lambda item: item[1], reverse=True)
    params, values = zip(*sorted_evppi)

    plt.figure(figsize=(10, 6))
    sns.barplot(x=list(values), y=list(params), hue=list(params), palette=palette, legend=False)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path)
        print(f"Plot saved to {output_path}")
    else:
        plt.show()


# ---------------------------------------------------------------------------
def plot_evppi_tornado(
    evppi_results: Dict[str, float],
    title: str = "Tornado Plot of EVPPI",
    output_path: Union[str, None] = None,
    color: str = "skyblue",
    xlabel: str = "EVPPI",
):
    """
    Generate a tornado plot of EVPPI results.

    A tornado plot is a type of bar chart that is used to visualize the
    sensitivity of a model's output to different input parameters. In this
    case, it shows the EVPPI for each parameter, sorted from lowest to highest.

    Args:
        evppi_results: A dictionary where keys are parameter names and
            values are their EVPPI.
        title: The title of the plot.
        output_path: The path to save the plot to. If None, the plot is
            displayed directly.
        color: The color of the bars.
        xlabel: The label for the x-axis.
    """
    if not evppi_results:
        print("No EVPPI results to plot.")
        return

    # Sort by value for better visualization
    sorted_evppi = sorted(evppi_results.items(), key=lambda item: item[1], reverse=False)
    params, values = zip(*sorted_evppi)

    plt.figure(figsize=(10, 6))
    y_pos = np.arange(len(params))
    plt.barh(y_pos, values, align="center", color=color)
    plt.yticks(y_pos, params)
    plt.xlabel(xlabel)
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
    "plot_evppi_tornado",
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
    "calculate_reynolds_smolensky_index",
    "calculate_budget_impact",
    "generate_microsim_report",
]
