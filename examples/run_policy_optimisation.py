"""
Example script for using the policy optimisation tool with Optuna.

This script demonstrates how to:
1. Load a population dataset.
2. Define metric functions for evaluation.
3. Load an optimisation study configuration from a YAML file.
4. Run the policy optimisation.
5. Print the results of the best trial found by Optuna.
"""

import os
from typing import Any, Callable

import pandas as pd
import yaml

from src.optimisation import run_policy_optimisation

# --- 1. Define Metric Functions ---
# These functions take a simulation result DataFrame and return a single number.


def total_tax_revenue(df: pd.DataFrame) -> float:
    """Calculates the total income tax paid by the population."""
    return df["tax_liability"].sum()


def total_wff_paid(df: pd.DataFrame) -> float:
    """Calculates the total Working for Families credits paid."""
    wff_columns = ["FTCcalc", "IWTCcalc", "BSTCcalc", "MFTCcalc"]
    existing_cols = [col for col in wff_columns if col in df.columns]
    return df[existing_cols].sum().sum()


# --- 2. Main Execution ---

if __name__ == "__main__":
    # Get the absolute path to the project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # --- Load Population Data ---
    input_data_path = os.path.join(project_root, "puf.csv")
    try:
        population_df = pd.read_csv(input_data_path)
    except FileNotFoundError:
        print(f"Error: Input data file not found at {input_data_path}")
        print("Please ensure the `puf.csv` file exists in the project root.")
        exit()

    if "income" in population_df.columns and "taxable_income" not in population_df.columns:
        population_df["taxable_income"] = population_df["income"]

    # --- Load Optimisation Configuration ---
    config_path = os.path.join(os.path.dirname(__file__), "opt_config.yaml")
    try:
        with open(config_path, "r") as f:
            opt_config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Optimisation configuration file not found at {config_path}")
        exit()

    # --- Define Metrics ---
    metrics_to_run: dict[str, Callable[[Any], float]] = {
        "total_tax_revenue": total_tax_revenue,
        "total_wff_paid": total_wff_paid,
    }

    # --- Run the Policy Optimisation ---
    print("Running policy optimisation study...")
    print("Base year: 2024-2025")
    print(f"Objective: {opt_config['objective']['direction']} '{opt_config['objective']['name']}'")
    print(f"Number of trials: {opt_config.get('n_trials', 100)}")

    base_simulation_year = "2024-2025"

    study = run_policy_optimisation(
        base_df=population_df, base_year=base_simulation_year, opt_config=opt_config, metrics=metrics_to_run
    )

    # --- Print Results ---
    print("\nOptimisation study complete.")
    print(f"Best trial number: {study.best_trial.number}")
    print(f"Best objective value ({opt_config['objective']['name']}): {study.best_value:,.2f}\n")

    print("Best parameters found:")
    for param, value in study.best_params.items():
        print(f"  - {param}: {value}")

    print("\nMetrics for the best trial:")
    # Retrieve all metrics stored in the user attributes of the best trial
    best_trial_metrics = study.best_trial.user_attrs.get("metrics", {})
    for metric_name, value in best_trial_metrics.items():
        print(f"  - {metric_name}: {value:,.2f}")
