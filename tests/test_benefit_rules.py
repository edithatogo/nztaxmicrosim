import pandas as pd
import pytest

from src.benefit_rules import (
    AccommodationSupplementRule,
    JSSRule,
    SLPRule,
    SPSRule,
)
from src.microsim import load_parameters


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


from src.benefit_rules import WEPRule


def test_wep_rule(sample_dataframe):
    """Test the WEPRule."""
    params = load_parameters("2023-2024")
    rule = WEPRule(wep_params=params.wep)
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


from src.benefit_rules import BSTCRule


def test_bstc_rule(sample_dataframe):
    """Test the BSTCRule."""
    params = load_parameters("2023-2024")
    rule = BSTCRule(bstc_params=params.bstc)
    df = sample_dataframe.copy()
    df["familyinc"] = [50000, 80000, 100000]
    df["ages_of_children"] = [[0], [2], [4]]
    data = {"df": df}
    rule(data)
    assert "bstc_entitlement" in data["df"].columns
    assert data["df"]["bstc_entitlement"][0] == 3640
    assert data["df"]["bstc_entitlement"][1] == 3640 - (80000 - 79000) * 0.21
    assert data["df"]["bstc_entitlement"][2] == 0
