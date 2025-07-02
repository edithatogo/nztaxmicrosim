import pandas as pd

from src.microsim import load_parameters
from src.wff_microsim import famsim


def main() -> None:
    """
    This is the main entry point for the Working for Families (WFF) microsimulation model.
    It demonstrates how to load parameters, create a sample DataFrame, and run the `famsim`
    function to calculate WFF entitlements. The results are then printed to the console.
    """
    # Load the data
    # df = pd.read_csv('data.csv')

    # For now, create a sample dataframe
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

    # Set the parameters for a specific year
    year = "2023-2024"
    params = load_parameters(year)
    wff_params = params["wff"]

    wagegwt: float = 0.0
    daysinperiod: int = 365

    # Call the famsim function
    result: pd.DataFrame = famsim(
        df,
        wff_params,
        wagegwt,
        daysinperiod,
    )

    # Print the results
    print(result)


if __name__ == "__main__":
    main()
