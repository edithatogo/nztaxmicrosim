import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.microsim import load_parameters, taxit
from src.sensitivity_analysis import run_deterministic_analysis, run_probabilistic_analysis
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


def plot_histogram(data: np.ndarray, title: str, save_path: str):
    """Generates and saves a histogram."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(data, bins=50, density=True, alpha=0.7)
    ax.set_xlabel("Total WFF Entitlement ($)")
    ax.set_ylabel("Density")
    ax.set_title(title)

    plt.tight_layout()
    plt.savefig(save_path)
    print(f"Histogram saved to {save_path}")


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

    # Define parameters to vary for DSA
    dsa_params_to_vary = [
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
        params_to_vary=dsa_params_to_vary,
        pct_change=0.10,
        population_df=population_df,
        output_metric_func=total_wff_entitlement,
        wff_runner=famsim,
        tax_runner=taxit,
    )

    print("--- Deterministic Sensitivity Analysis Results ---")
    print(dsa_results)

    # Generate and save the Tornado plot
    plot_tornado(
        dsa_results, "Deterministic Sensitivity Analysis of WFF Entitlements", "examples/reports/dsa_tornado_plot.png"
    )

    # Define parameter distributions for PSA
    psa_param_distributions = {
        "wff.ftc1": {"dist": "norm", "loc": 6642, "scale": 100},
        "wff.abaterate1": {"dist": "uniform", "loc": 0.25, "scale": 0.05},
        "tax_brackets.rates.0": {"dist": "norm", "loc": 0.105, "scale": 0.01},
    }

    # Run Probabilistic Sensitivity Analysis
    psa_results = run_probabilistic_analysis(
        param_distributions=psa_param_distributions,
        num_samples=1000,
        population_df=population_df,
        output_metric_func=total_wff_entitlement,
        wff_runner=famsim,
        tax_runner=taxit,
    )

    print("--- Probabilistic Sensitivity Analysis Results ---")
    print(f"Mean entitlement: ${psa_results.mean():.2f}")
    print(f"Standard deviation: ${psa_results.std():.2f}")

    # Generate and save the Histogram
    plot_histogram(
        psa_results,
        "Probabilistic Sensitivity Analysis of WFF Entitlements",
        "examples/reports/psa_histogram.png",
    )


if __name__ == "__main__":
    main()
