import pandas as pd
import pytest

from src.benefit_rules import (
    AccommodationSupplementRule,
    BSTCRule,
    FTCRule,
    IWTCRule,
    JSSRule,
    MFTCRule,
    SLPRule,
    SPSRule,
    WEPRule,
)
from src.microsim import load_parameters
from src.parameters import BSTCParams, FTCParams, IWTCParams, MFTCParams, WEPParams


@pytest.fixture
def sample_dataframe():
    """A sample dataframe for testing the benefit rules."""
    data = {
        "total_individual_income_weekly": [500, 1000, 200],
        "marital_status": ["Single", "Married", "Single"],
        "num_children": [0, 2, 0],
        "disability_status": [False, False, True],
        "household_size": [1, 4, 1],
        "housing_costs": [200, 500, 250],
        "region": ["Auckland", "Wellington", "Canterbury"],
    }
    return pd.DataFrame(data)


def test_jss_rule(sample_dataframe):
    """Test the JSSRule."""
    params = load_parameters("2023-2024")
    rule = JSSRule(jss_params=params.jss)
    data = {"df": sample_dataframe.copy()}
    rule(data)
    assert "jss_entitlement" in data["df"].columns


def test_sps_rule(sample_dataframe):
    """Test the SPSRule."""
    params = load_parameters("2023-2024")
    rule = SPSRule(sps_params=params.sps)
    data = {"df": sample_dataframe.copy()}
    rule(data)
    assert "sps_entitlement" in data["df"].columns


def test_slp_rule(sample_dataframe):
    """Test the SLPRule."""
    params = load_parameters("2023-2024")
    rule = SLPRule(slp_params=params.slp)
    data = {"df": sample_dataframe.copy()}
    rule(data)
    assert "slp_entitlement" in data["df"].columns


def test_accommodation_supplement_rule(sample_dataframe):
    """Test the AccommodationSupplementRule."""
    params = load_parameters("2023-2024")
    rule = AccommodationSupplementRule(as_params=params.accommodation_supplement)
    data = {"df": sample_dataframe.copy()}
    rule(data)
    assert "accommodation_supplement_entitlement" in data["df"].columns


def test_wep_rule(sample_dataframe):
    """Test the WEPRule."""
    params = load_parameters("2023-2024")
    wep_params = params.wep
    if wep_params is None:
        wep_params = WEPParams(single_rate=20.46, couple_rate=31.82, child_rate=0.0)
    rule = WEPRule(wep_params=wep_params)
    df = sample_dataframe.copy()
    df["is_jss_recipient"] = [True, False, False]
    df["is_sps_recipient"] = [False, False, False]
    df["is_slp_recipient"] = [False, False, True]
    df["is_nz_super_recipient"] = [False, True, False]
    data = {"df": df}
    rule(data)
    assert "wep_entitlement" in data["df"].columns
    assert data["df"]["wep_entitlement"][0] == 20.46
    assert data["df"]["wep_entitlement"][1] == 31.82
    assert data["df"]["wep_entitlement"][2] == 20.46


def test_bstc_rule(sample_dataframe):
    """Test the BSTCRule."""
    params = load_parameters("2023-2024")
    bstc_params = params.bstc
    if bstc_params is None:
        bstc_params = BSTCParams(threshold=79000, rate=0.21, amount=3640, max_age=3)
    rule = BSTCRule(bstc_params=bstc_params)
    df = sample_dataframe.copy()
    df["familyinc"] = [50000, 80000, 100000]
    df["ages_of_children"] = [[0], [2], [4]]
    data = {"df": df}
    rule(data)
    assert "bstc_entitlement" in data["df"].columns
    assert data["df"]["bstc_entitlement"][0] == 3640
    assert data["df"]["bstc_entitlement"][1] == 3640 - (80000 - 79000) * 0.21
    assert data["df"]["bstc_entitlement"][2] == 0


def test_ftc_rule(sample_dataframe):
    """Test the FTCRule."""
    params = load_parameters("2023-2024")
    ftc_params = params.ftc
    if ftc_params is None:
        ftc_params = FTCParams(base_rate=6645, child_rate=5415, income_threshold=42700, abatement_rate=0.27)
    rule = FTCRule(ftc_params=ftc_params)
    df = sample_dataframe.copy()
    df["familyinc"] = [40000, 50000, 100000]
    df["num_children"] = [1, 2, 3]
    data = {"df": df}
    rule(data)
    assert "ftc_entitlement" in data["df"].columns
    assert data["df"]["ftc_entitlement"][0] == 6645
    assert data["df"]["ftc_entitlement"][1] == 6645 + 5415 - (50000 - 42700) * 0.27
    assert data["df"]["ftc_entitlement"][2] == 6645 + 2 * 5415 - (100000 - 42700) * 0.27


def test_iwtc_rule(sample_dataframe):
    """Test the IWTCRule."""
    params = load_parameters("2023-2024")
    iwtc_params = params.iwtc
    if iwtc_params is None:
        iwtc_params = IWTCParams(
            base_rate=3770,
            child_rate=780,
            income_threshold=42700,
            abatement_rate=0.27,
            min_hours_worked=20,
        )
    rule = IWTCRule(iwtc_params=iwtc_params)
    df = sample_dataframe.copy()
    df["familyinc"] = [40000, 50000, 100000]
    df["num_children"] = [1, 2, 3]
    df["hours_worked"] = [25, 30, 10]
    data = {"df": df}
    rule(data)
    assert "iwtc_entitlement" in data["df"].columns
    assert data["df"]["iwtc_entitlement"][0] == 3770
    assert data["df"]["iwtc_entitlement"][1] == 3770 + 780 - (50000 - 42700) * 0.27
    assert data["df"]["iwtc_entitlement"][2] == 0


def test_mftc_rule(sample_dataframe):
    """Test the MFTCRule."""
    params = load_parameters("2023-2024")
    mftc_params = params.mftc
    if mftc_params is None:
        mftc_params = MFTCParams(guaranteed_income=34320)
    rule = MFTCRule(mftc_params=mftc_params)
    df = sample_dataframe.copy()
    df["familyinc"] = [30000, 40000, 50000]
    df["tax_liability"] = [3000, 5000, 8000]
    data = {"df": df}
    rule(data)
    assert "mftc_entitlement" in data["df"].columns
    assert data["df"]["mftc_entitlement"][0] == 34320 - (30000 - 3000)
    assert data["df"]["mftc_entitlement"][1] == 0
    assert data["df"]["mftc_entitlement"][2] == 0
