import argparse
import os
import sys

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.microsim import load_parameters
from src.reporting import generate_microsim_report


def generate_reports():
    """
    Loads the microsimulation results and generates comprehensive reports.
    
    This function generates publication-quality tables and plots with natural language labels
    for policy analysis. It now uses the SQLite parameter database instead of JSON files.
    
    Usage:
        python examples/generate_reports.py --years 2023-2024 2024-2025
    """
    print("--- Generating Comprehensive Reports ---")

    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(description="Generate reports from microsimulation results.")
    parser.add_argument(
        "--years",
        nargs="+",
        type=str,
        default=["2024-2025"],
        help="Tax years to generate reports for (e.g., 2024-2025).",
    )
    args = parser.parse_args()

    # --- Load Data and Parameters for each year ---
    all_dfs = {}
    for year in args.years:
        results_filename = f"synthetic_population_results_{year.replace('-', '_')}.csv"
        results_path = os.path.join("examples", "synthetic_population", results_filename)

        if not os.path.exists(results_path):
            print(f"Error: Results file not found at {results_path} for year {year}")
            print("Please run 'run_microsim_with_synthetic_population.py' for this year first.")
            continue

        df_year = pd.read_csv(results_path)
        df_year["year"] = year  # Add a 'year' column for easy comparison
        all_dfs[year] = df_year

    if not all_dfs:
        print("No data loaded for reporting. Exiting.")
        return

    # Concatenate all dataframes for combined analysis
    df = pd.concat(all_dfs.values(), ignore_index=True)

    # Define abatement thresholds from the first year's parameters
    first_year = args.years[0]
    first_year_params = load_parameters(first_year)
    abatethresh1 = first_year_params.wff.abatethresh1 if first_year_params.wff else 42700
    abatethresh2 = first_year_params.wff.abatethresh2 if first_year_params.wff else 80000
    bstcthresh = first_year_params.wff.bstcthresh if first_year_params.wff else 79000

    # Prepare data for the new reporting framework
    # The reporting framework expects 'disposable_income' and 'disposable_income_ahc'
    # to be present in the DataFrame.
    # For now, we'll add dummy columns if they don't exist, or calculate them if possible.
    # In a full integration, these would be calculated during the microsimulation run.

    # Placeholder for disposable income calculation if not already present
    if "disposable_income" not in df.columns:
        df["disposable_income"] = (
            df["employment_income"]
            + df["self_employment_income"]
            + df["investment_income"]
            + df["rental_property_income"]
            + df["private_pensions_annuities"]
            + df["jss_entitlement"] * 52  # Annualize weekly benefits
            + df["sps_entitlement"] * 52
            + df["slp_entitlement"] * 52
            + df["accommodation_supplement_entitlement"] * 52
            + df["FTCcalc"]  # WFF components are already annual
            + df["IWTCcalc"]
            + df["BSTCcalc"]
            + df["MFTCcalc"]
            - df["income_tax_payable"]  # Assuming income_tax_payable is annual
        )

    if "housing_costs" in df.columns and "disposable_income_ahc" not in df.columns:
        df["disposable_income_ahc"] = df["disposable_income"] - (df["housing_costs"] * 52)
    elif "disposable_income_ahc" not in df.columns:
        df["disposable_income_ahc"] = df["disposable_income"]  # If no housing costs, AHC is same as disposable

    # Define report parameters
    report_params = {
        "poverty_line_relative": 0.6,  # Example: 60% of median income for poverty line
        "abatethresh1": abatethresh1,
        "abatethresh2": abatethresh2,
        "bstcthresh": bstcthresh,
    }

    # Generate the report using the new framework
    generate_microsim_report(df, report_params)

    print("\n--- Reporting Complete ---")


if __name__ == "__main__":
    generate_reports()
