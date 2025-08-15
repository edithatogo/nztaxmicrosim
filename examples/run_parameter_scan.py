"""
Example script for using the parameter scanning tool.

This script demonstrates how to:
1. Load a population dataset.
2. Define metric functions for evaluation.
3. Load a scenario configuration from a YAML file.
4. Run the parameter scan using these components.
5. Print the summary of results.
"""

<<<<<<< HEAD
import os

import pandas as pd
import yaml

from src.optimisation import run_parameter_scan
=======
import pandas as pd
import yaml
from src.optimisation import run_parameter_scan
import os
>>>>>>> origin/update-a-bunch-of-stuff-5

# --- 1. Define Metric Functions ---
# These functions take a simulation result DataFrame and return a single number.

<<<<<<< HEAD

=======
>>>>>>> origin/update-a-bunch-of-stuff-5
def total_tax_revenue(df: pd.DataFrame) -> float:
    """Calculates the total income tax paid by the population."""
    return df["tax_liability"].sum()

<<<<<<< HEAD

=======
>>>>>>> origin/update-a-bunch-of-stuff-5
def total_wff_paid(df: pd.DataFrame) -> float:
    """Calculates the total Working for Families credits paid."""
    wff_columns = ["FTCcalc", "IWTCcalc", "BSTCcalc", "MFTCcalc"]
    # Ensure columns exist before summing
    existing_cols = [col for col in wff_columns if col in df.columns]
    return df[existing_cols].sum().sum()

<<<<<<< HEAD

=======
>>>>>>> origin/update-a-bunch-of-stuff-5
# --- 2. Main Execution ---

if __name__ == "__main__":
    # Get the absolute path to the project root
<<<<<<< HEAD
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
=======
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
>>>>>>> origin/update-a-bunch-of-stuff-5

    # --- Load Population Data ---
    # Using the same public use file as other examples.
    # In a real analysis, this would be a more detailed microdata file.
<<<<<<< HEAD
    input_data_path = os.path.join(project_root, "puf.csv")
=======
    input_data_path = os.path.join(project_root, 'puf.csv')
>>>>>>> origin/update-a-bunch-of-stuff-5
    try:
        population_df = pd.read_csv(input_data_path)
    except FileNotFoundError:
        print(f"Error: Input data file not found at {input_data_path}")
        print("Please ensure the `puf.csv` file exists in the project root.")
        exit()

    # The scanner requires a 'taxable_income' column. Let's assume 'income' is it.
<<<<<<< HEAD
    if "income" in population_df.columns and "taxable_income" not in population_df.columns:
        population_df["taxable_income"] = population_df["income"]

    # --- Load Scan Configuration ---
    config_path = os.path.join(os.path.dirname(__file__), "scan_config.yaml")
    try:
        with open(config_path, "r") as f:
=======
    if 'income' in population_df.columns and 'taxable_income' not in population_df.columns:
        population_df['taxable_income'] = population_df['income']

    # --- Load Scan Configuration ---
    config_path = os.path.join(os.path.dirname(__file__), 'scan_config.yaml')
    try:
        with open(config_path, 'r') as f:
>>>>>>> origin/update-a-bunch-of-stuff-5
            scan_config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Scan configuration file not found at {config_path}")
        exit()

    # --- Define Metrics ---
<<<<<<< HEAD
    metrics_to_run = {"Total Tax Revenue": total_tax_revenue, "Total WFF Paid": total_wff_paid}

    # --- Run the Parameter Scan ---
    print("Running parameter scan...")
    print("Base year: 2024-2025")
=======
    metrics_to_run = {
        "Total Tax Revenue": total_tax_revenue,
        "Total WFF Paid": total_wff_paid
    }

    # --- Run the Parameter Scan ---
    print("Running parameter scan...")
    print(f"Base year: 2024-2025")
>>>>>>> origin/update-a-bunch-of-stuff-5
    print(f"Scenarios to run: {[s['id'] for s in scan_config['scenarios']]}\n")

    # The base year for parameters
    base_simulation_year = "2024-2025"

    results_df = run_parameter_scan(
<<<<<<< HEAD
        base_df=population_df, base_year=base_simulation_year, scan_config=scan_config, metrics=metrics_to_run
=======
        base_df=population_df,
        base_year=base_simulation_year,
        scan_config=scan_config,
        metrics=metrics_to_run
>>>>>>> origin/update-a-bunch-of-stuff-5
    )

    # --- Print Results ---
    print("Parameter Scan Results:")
    print(results_df.to_string())
