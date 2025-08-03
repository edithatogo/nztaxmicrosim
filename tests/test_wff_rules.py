import pandas as pd
import pytest

from src.microsim import load_parameters
from src.wff_rules import (
    ApplyCalibrationsRule,
    ApplyCareLogicRule,
    CalculateAbatementRule,
    CalculateMaxEntitlementsRule,
    GrossUpIncomeRule,
)


@pytest.fixture
def sample_dataframe():
    """A sample dataframe for testing the WFF rules."""
    data = {
        "familyinc": [70000],
        "FTCwgt": [2],
        "IWTCwgt": [2],
        "BSTC0wgt": [0],
        "BSTC01wgt": [0],
        "BSTC1wgt": [1],
        "MFTCwgt": [0],
        "iwtc_elig": [1],
        "pplcnt": [4],
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
    return pd.DataFrame(data)


def test_gross_up_income_rule(sample_dataframe):
    """Test the GrossUpIncomeRule."""
    rule = GrossUpIncomeRule(wagegwt=0.1)
    data = {"df": sample_dataframe.copy()}
    rule(data)
    assert "familyinc_grossed_up" in data["df"].columns
    assert data["df"]["familyinc_grossed_up"].iloc[0] == 77000


def test_calculate_abatement_rule(sample_dataframe):
    """Test the CalculateAbatementRule."""
    params = load_parameters("2023-2024")
    rule = CalculateAbatementRule(wff_params=params.wff, daysinperiod=365)
    sample_dataframe["familyinc_grossed_up"] = sample_dataframe["familyinc"]
    data = {"df": sample_dataframe.copy()}
    rule(data)
    assert "abate_amt" in data["df"].columns


def test_calculate_max_entitlements_rule(sample_dataframe):
    """Test the CalculateMaxEntitlementsRule."""
    params = load_parameters("2023-2024")
    rule = CalculateMaxEntitlementsRule(wff_params=params.wff)
    sample_dataframe["familyinc_grossed_up"] = sample_dataframe["familyinc"]
    data = {"df": sample_dataframe.copy()}
    rule(data)
    assert "maxFTCent" in data["df"].columns


def test_apply_care_logic_rule(sample_dataframe):
    """Test the ApplyCareLogicRule."""
    params = load_parameters("2023-2024")
    rule = ApplyCareLogicRule(wff_params=params.wff)
    # Add required columns
    sample_dataframe["maxFTCent"] = 100
    sample_dataframe["maxIWTCent"] = 50
    sample_dataframe["maxBSTC0ent"] = 0
    sample_dataframe["maxBSTC01ent"] = 0
    sample_dataframe["maxBSTC1ent"] = 20
    sample_dataframe["maxMFTCent"] = 0
    sample_dataframe["abate_amt"] = 10
    sample_dataframe["BSTCabate_amt"] = 5
    data = {"df": sample_dataframe.copy()}
    rule(data)
    assert "FTCcalc" in data["df"].columns


def test_apply_calibrations_rule(sample_dataframe):
    """Test the ApplyCalibrationsRule."""
    rule = ApplyCalibrationsRule()
    sample_dataframe["IWTCcalc"] = 100
    sample_dataframe["selfempind"] = 1
    sample_dataframe["iwtc"] = 0
    data = {"df": sample_dataframe.copy()}
    rule(data)
    assert data["df"]["IWTCcalc"].iloc[0] == 0
