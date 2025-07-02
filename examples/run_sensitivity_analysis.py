import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.microsim import load_parameters
from src.sensitivity_analysis import run_deterministic_analysis
from src.wff_microsim import famsim


def total_wff_entitlement(df: pd.DataFrame) -> float:
    """Calculates the total WFF entitlement from a simulation result."""
    return df[["FTCcalc", "IWTCcalc", "BSTCcalc", "MFTCcalc"]].sum().sum()


def plot_tornado(df: pd.DataFrame, title: str, save_path: str):
    """Generates and saves a tornado plot."""
    df["range"] = df["high_value"] - df["low_value"]
    df = df.reindex(df["range"].abs().sort_values().index)

    fig, ax = plt.subplots(figsize=(10, 8))
    y_pos = np.arange(len(df))

    ax.barh(y_pos, df["range"], align="center")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(df["parameter"])
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel("Impact on Total WFF Entitlement ($)")
    ax.set_title(title)

    plt.tight_layout()
    plt.savefig(save_path)
    print(f"Tornado plot saved to {save_path}")


def main():
    """Main function to run the sensitivity analysis."""
    # Load baseline parameters
    year = "2023-2024"
    baseline_params = load_parameters(year)

    # Create a sample population
    population_df = pd.DataFrame(
        {
            "familyinc": np.random.uniform(20000, 150000, size=1000),
            "FTCwgt": np.random.randint(0, 4, size=1000),
            "IWTCwgt": np.random.randint(0, 4, size=1000),
            "BSTC0wgt": np.random.randint(0, 2, size=1000),
            "BSTC01wgt": np.random.randint(0, 2, size=1000),
            "BSTC1wgt": np.random.randint(0, 2, size=1000),
            "MFTCwgt": np.random.randint(0, 2, size=1000),
            "iwtc_elig": 12,
            "pplcnt": 0,
            "MFTC_total": 1000,
            "MFTC_elig": 1,
            "sharedcare": 0,
            "sharecareFTCwgt": 0,
            "sharecareBSTC0wgt": 0,
            "sharecareBSTC01wgt": 0,
            "sharecareBSTC1wgt": 0,
            "iwtc": 1,
            "selfempind": 0,
            "maxkiddays": 365,
            "maxkiddaysbstc": 365,
        }
    )

    # Define parameters to vary
    params_to_vary = [
        "wff.ftc1",
        "wff.ftc2",
        "wff.iwtc1",
        "wff.abatethresh1",
        "wff.abaterate1",
        "tax_brackets.rates.0",
        "tax_brackets.rates.1",
        "tax_brackets.thresholds.0",
    ]

    # Run Deterministic Sensitivity Analysis
    dsa_results = run_deterministic_analysis(
        baseline_params=baseline_params,
        params_to_vary=params_to_vary,
        pct_change=0.10,
        population_df=population_df,
        output_metric_func=total_wff_entitlement,
        wff_runner=famsim,
    )

    print("--- Deterministic Sensitivity Analysis Results ---")
    print(dsa_results)

    # Generate and save the Tornado plot
    plot_tornado(
        dsa_results, "Deterministic Sensitivity Analysis of WFF Entitlements", "examples/reports/dsa_tornado_plot.png"
    )


if __name__ == "__main__":
    main()
