"""Unit tests for the Working for Families microsimulation functions."""

import numpy as np
import pandas as pd
import pytest

from src.microsim import load_parameters
from src.wff_logic import (
    apply_calibrations,
    apply_care_logic,
    calculate_abatement,
    calculate_max_entitlements,
    gross_up_income,
)
from src.wff_microsim import famsim

params_2022_23 = load_parameters("2022-2023")


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Return a sample dataframe used across tests."""
    return pd.DataFrame(
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


def test_gross_up_income(sample_df: pd.DataFrame) -> None:
    df = gross_up_income(sample_df, 0.1)
    assert np.allclose(df["familyinc_grossed_up"], sample_df["familyinc"] * 1.1)


def test_calculate_abatement(sample_df: pd.DataFrame) -> None:
    df = gross_up_income(sample_df, 0)
    df = calculate_abatement(df, params_2022_23.wff, 365)
    assert np.allclose(df["abate_amt"], np.array([1971.0, 15471.0, 0.0]))
    assert np.allclose(df["BSTCabate_amt"], np.array([0.0, 4410.0, 0.0]))


def test_calculate_max_entitlements(sample_df: pd.DataFrame) -> None:
    df = gross_up_income(sample_df, 0)
    df = calculate_max_entitlements(df, params_2022_23.wff)
    assert np.allclose(df["maxFTCent"], np.array([6642.0, 12054.0, 0.0]))
    assert np.allclose(df["maxIWTCent"], np.array([3770.0, 3770.0, 0.0]))
    assert np.allclose(df["maxBSTC0ent"], np.array([3388.0, 0.0, 0.0]))
    assert np.allclose(df["maxBSTC01ent"], np.array([0.0, 3388.0, 0.0]))
    assert np.allclose(df["maxBSTC1ent"], np.array([0.0, 0.0, 3388.0]))
    assert np.allclose(df["maxMFTCent"], np.array([0.0, 0.0, 1000.0]))


def test_apply_care_logic(sample_df: pd.DataFrame) -> None:
    wff_params = params_2022_23.wff
    df = gross_up_income(sample_df, 0)
    df = calculate_abatement(df, wff_params, 365)
    df = calculate_max_entitlements(df, wff_params)
    df = apply_care_logic(df, wff_params)
    expected_FTCcalc = np.array([4671.0, 0.0, 0.0])
    expected_IWTCcalc = np.array([3770.0, 353.0, 0.0])
    expected_BSTCcalc = np.array([3388.0, 3388.0, 3388.0])
    expected_MFTCcalc = np.array([0.0, 0.0, 1000.0])
    assert np.allclose(df["FTCcalc"], expected_FTCcalc)
    assert np.allclose(df["IWTCcalc"], expected_IWTCcalc)
    assert np.allclose(df["BSTCcalc"], expected_BSTCcalc)
    assert np.allclose(df["MFTCcalc"], expected_MFTCcalc)


def test_apply_calibrations() -> None:
    df = pd.DataFrame({"IWTCcalc": [100.0], "iwtc": [0], "selfempind": [1]})
    df = apply_calibrations(df)
    assert df.loc[0, "IWTCcalc"] == 0


def test_famsim(sample_df: pd.DataFrame) -> None:
    wff_params = params_2022_23.wff
    result = famsim(sample_df.copy(), wff_params, 0, 365)
    expected_FTCcalc = np.array([4671.0, 0.0, 0.0])
    expected_IWTCcalc = np.array([3770.0, 353.0, 0.0])
    expected_BSTCcalc = np.array([3388.0, 3388.0, 3388.0])
    expected_MFTCcalc = np.array([0.0, 0.0, 1000.0])
    assert np.allclose(result["FTCcalc"], expected_FTCcalc)
    assert np.allclose(result["IWTCcalc"], expected_IWTCcalc)
    assert np.allclose(result["BSTCcalc"], expected_BSTCcalc)
    assert np.allclose(result["MFTCcalc"], expected_MFTCcalc)
