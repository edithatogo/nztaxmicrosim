import pandas as pd

from .reporting_framework import FiscalImpactTable


_fiscal_helper = FiscalImpactTable()


def calculate_budget_impact(baseline_df: pd.DataFrame, reform_df: pd.DataFrame) -> pd.DataFrame:
    """Compare baseline and reform fiscal outcomes.

    Parameters
    ----------
    baseline_df : pd.DataFrame
        Data for the baseline scenario.
    reform_df : pd.DataFrame
        Data for the reform scenario.

    Returns
    -------
    pd.DataFrame
        Table with baseline, reform and difference in revenue and spending.
    """
    baseline_tax = _fiscal_helper._calculate_total_tax_revenue(baseline_df)
    baseline_welfare = _fiscal_helper._calculate_total_welfare_transfers(baseline_df)
    baseline_net = _fiscal_helper._calculate_net_fiscal_impact(baseline_tax, baseline_welfare)

    reform_tax = _fiscal_helper._calculate_total_tax_revenue(reform_df)
    reform_welfare = _fiscal_helper._calculate_total_welfare_transfers(reform_df)
    reform_net = _fiscal_helper._calculate_net_fiscal_impact(reform_tax, reform_welfare)

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


__all__ = ["calculate_budget_impact"]
