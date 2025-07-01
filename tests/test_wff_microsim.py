"""
Unit tests for the Working for Families (WFF) microsimulation model.

This module contains tests for the `famsim` function defined in `src/wff_microsim.py`,
ensuring its correctness and adherence to the original SAS model logic.
"""

import numpy as np
import pandas as pd

from src.microsim import load_parameters
from src.wff_microsim import famsim

# Load parameters for testing
params_2023_24 = load_parameters("2023-2024")


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
    wff_params = params_2023_24["wff"]
    wagegwt = 0
    daysinperiod = 365

    # Call the function
    result = famsim(
        df,
        wff_params,
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


def test_famsim_abatement():
    """
    Tests the famsim function with a focus on the abatement calculation.
    """
    # Create a sample dataframe
    df = pd.DataFrame(
        {
            "familyinc": [50000],
            "FTCwgt": [1],
            "IWTCwgt": [1],
            "BSTC0wgt": [0],
            "BSTC01wgt": [0],
            "BSTC1wgt": [0],
            "MFTCwgt": [0],
            "iwtc_elig": [12],
            "pplcnt": [0],
            "MFTC_total": [0],
            "MFTC_elig": [0],
            "sharedcare": [0],
            "sharecareFTCwgt": [0],
            "sharecareBSTC0wgt": [0],
            "sharecareBSTC01wgt": [0],
            "sharecareBSTC1wgt": [0],
            "iwtc": [1],
            "selfempind": [0],
            "maxkiddays": [365],
            "maxkiddaysbstc": [365],
        }
    )

    # Set the parameters
    wff_params = params_2023_24["wff"]
    wagegwt = 0
    daysinperiod = 365

    # Call the function
    result = famsim(
        df,
        wff_params,
        wagegwt,
        daysinperiod,
    )

    # Assert the results
    expected_abate_amt = (50000 - wff_params["abatethresh1"]) * wff_params["abaterate1"]
    expected_FTCcalc = max(0, wff_params["ftc1"] - expected_abate_amt)
    expected_carryforward_abate = expected_abate_amt - (wff_params["ftc1"] - expected_FTCcalc)
    expected_IWTCcalc = max(0, wff_params["iwtc1"] - expected_carryforward_abate)

    assert np.allclose(result["abate_amt"], expected_abate_amt)
    assert np.allclose(result["FTCcalc"], expected_FTCcalc)
    assert np.allclose(result["carryforward_abate"], expected_carryforward_abate)
    assert np.allclose(result["IWTCcalc"], expected_IWTCcalc)
