import os
import sys

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import glob

from src.microsim import load_parameters
from src.wff_microsim import famsim


def run_validation():
    """
    Runs the WFF microsimulation for all available parameter files and generates a report.
    """
    # Get a list of all parameter files
    param_files = glob.glob("src/parameters_*.json")
    param_files.sort()

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

    # Iterate over the parameter files
    for param_file in param_files:
        # Extract the year from the filename
        year = os.path.basename(param_file).replace("parameters_", "").replace(".json", "")

        # Load the parameters
        params = load_parameters(year)
        wff_params = params["wff"]

        # Run the simulation
        result_df = famsim(
            df.copy(),
            wff_params,
            wagegwt,
            daysinperiod,
        )

        # Store the results
        results.append({"year": year, "result": result_df.to_string()})

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
