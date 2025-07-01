import pandas as pd

from src.wff_microsim import famsim


def main() -> None:
    """
    This is the main entry point for the WFF microsimulation model.
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

    # Set the parameters
    ftc1: float = 6642.0
    ftc2: float = 5412.0
    iwtc1: float = 3770.0
    iwtc2: float = 780.0
    bstc: float = 3388.0
    mftc: float = 38627.0
    abatethresh1: float = 42700.0
    abatethresh2: float = 80000.0
    abaterate1: float = 0.27
    abaterate2: float = 0.27
    bstcthresh: float = 79000.0
    bstcabate: float = 0.21
    wagegwt: float = 0.0
    daysinperiod: int = 365

    # Call the famsim function
    result: pd.DataFrame = famsim(
        df,
        ftc1,
        ftc2,
        iwtc1,
        iwtc2,
        bstc,
        mftc,
        abatethresh1,
        abatethresh2,
        abaterate1,
        abaterate2,
        bstcthresh,
        bstcabate,
        wagegwt,
        daysinperiod,
    )

    # Print the results
    print(result)


if __name__ == "__main__":
    main()
