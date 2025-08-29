import os
import sqlite3
import sys

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.microsim import load_parameters
from src.wff_microsim import famsim


def get_available_years():
    """Get all available years from the SQLite database."""
    db_path = os.path.join(os.path.dirname(__file__), "..", "src", "data", "parameters.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT year FROM policy_parameters WHERE policy_key = 'wff' ORDER BY year")
    years = [f"{row[0]}-{row[0] + 1}" for row in cursor.fetchall()]
    conn.close()
    return years


def run_validation():
    """
    Runs the WFF microsimulation for all available years from the SQLite database and generates a report.
    
    This function:
    1. Queries the SQLite parameter database to find all years with WFF parameters
    2. Runs the WFF microsimulation for each available year
    3. Generates a comprehensive validation report in Markdown format
    
    The report is saved to docs/validation_report.md
    """
    # Get available years from the database
    available_years = get_available_years()
    if not available_years:
        print("No WFF parameters found in the database.")
        return

    # Create a list to store the results
    results = []

    # Create a sample dataframe
    df: pd.DataFrame = pd.DataFrame(
        {
            "familyinc": [50000, 100000, 30000],
            "FTCwgt": [1, 2, 0],
            "IWTCwgt": [1, 2, 0],
            "BSTC0wgt": [1, 0, 0],
            "BSTC01wgt": [0, 1, 0],
            "BSTC1wgt": [0, 0, 1],
            "MFTCwgt": [1, 0, 0],
            "iwtc_elig": [12, 12, 12],
            "pplcnt": [0, 0, 0],
            "MFTC_total": [1000, 1000, 1000],
            "MFTC_elig": [1, 1, 1],
            "sharedcare": [0, 1, 0],
            "sharecareFTCwgt": [0, 1, 0],
            "sharecareBSTC0wgt": [0, 0, 0],
            "sharecareBSTC01wgt": [0, 1, 0],
            "sharecareBSTC1wgt": [0, 0, 0],
            "iwtc": [1, 1, 0],
            "selfempind": [0, 1, 0],
            "maxkiddays": [365, 365, 365],
            "maxkiddaysbstc": [365, 365, 365],
        }
    )

    wagegwt: float = 0.0
    daysinperiod: int = 365

    # Iterate over the available years
    for year in available_years:
        print(f"Running validation for year: {year}")
        
        try:
            # Load the parameters
            params = load_parameters(year)
            wff_params = params.wff
            
            if wff_params is None:
                print(f"WFF parameters not found for year {year}. Skipping.")
                continue

            # Run the simulation
            result_df = famsim(
                df.copy(),
                year=year,
                wagegwt=wagegwt,
                daysinperiod=daysinperiod,
            )

            # Store the results
            results.append({"year": year, "result": result_df.to_string()})
        except Exception as e:
            print(f"Error processing year {year}: {e}")
            results.append({"year": year, "result": f"Error: {e}"})

    # Generate the report
    with open("docs/validation_report.md", "w") as f:
        f.write("# WFF Microsimulation Validation Report\n\n")
        f.write(
            "This report shows the results of running the WFF microsimulation for each available parameter file.\n\n"
        )
        for result in results:
            f.write(f"## {result['year']}\n\n")
            f.write("```\n")
            f.write(result["result"])
            f.write("\n```\n\n")
        f.write("Verification link: [validation_report.md](docs/validation_report.md)")


if __name__ == "__main__":
    run_validation()
