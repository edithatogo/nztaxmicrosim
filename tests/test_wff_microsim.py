"""
Unit tests for the Working for Families (WFF) microsimulation model.

This module contains tests for the `famsim` function defined in `src/wff_microsim.py`,
ensuring its correctness and adherence to the original SAS model logic.
"""
import numpy as np
import pandas as pd

from src.wff_microsim import famsim


def test_famsim():
    """
    Tests the famsim function with a sample dataframe and parameters.
    Verifies the calculated FTC, IWTC, BSTC, and MFTC entitlements.
    """
    # Create a sample dataframe
    df = pd.DataFrame(
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
    ftc1 = 6642
    ftc2 = 5412
    iwtc1 = 3770
    iwtc2 = 780
    bstc = 3388
    mftc = 38627
    abatethresh1 = 42700
    abatethresh2 = 80000
    abaterate1 = 0.27
    abaterate2 = 0.27
    bstcthresh = 79000
    bstcabate = 0.21
    wagegwt = 0
    daysinperiod = 365

    # Call the function
    result = famsim(
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

    # Assert the results
    expected_FTCcalc = np.array([4671.0, 0.0, 0.0])
    expected_IWTCcalc = np.array([3770.0, 353.0, 0.0])
    expected_BSTCcalc = np.array([3388.0, 3388.0, 3388.0])
    expected_MFTCcalc = np.array([0.0, 0.0, 1000.0])

    assert np.allclose(result["FTCcalc"], expected_FTCcalc)
    assert np.allclose(result["IWTCcalc"], expected_IWTCcalc)
    assert np.allclose(result["BSTCcalc"], expected_BSTCcalc)
    assert np.allclose(result["MFTCcalc"], expected_MFTCcalc)
