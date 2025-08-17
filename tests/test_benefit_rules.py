"""Tests for the benefit rules."""

import pandas as pd
import pytest

from src.benefit_rules import (
    AccommodationSupplementRule,
    BSTCRule,
    DisabilityAllowanceRule,
    FTCRule,
    IWTCRule,
    JSSRule,
    MFTCRule,
    SLPRule,
    SPSRule,
    WEPRule,
)
from src.microsim import load_parameters


@pytest.fixture
def sample_dataframe():
    """A sample DataFrame for testing benefit rules."""
    return pd.DataFrame(
        {
            "total_individual_income_weekly": [500, 1000, 200],
            "marital_status": ["Single", "Married", "Single"],
            "num_children": [0, 2, 1],
            "disability_status": [False, False, True],
            "disability_costs": [0, 0, 50],
            "family_household_type": ["single_18_plus", "couple", "single_18_plus"],
            "household_size": [1, 4, 2],
            "housing_costs": [200, 400, 250],
            "region": ["Auckland", "Wellington", "Christchurch"],
            "hours_worked": [40, 40, 0],
            "ages_of_children": [[], [5, 8], [2]],
            "familyinc": [26000, 52000, 10400],
            "tax_liability": [2000, 5000, 800],
            "is_jss_recipient": [False, False, True],
            "is_sps_recipient": [False, False, False],
            "is_slp_recipient": [False, False, False],
            "is_nz_super_recipient": [False, False, False],
        }
    )


def test_jss_rule(sample_dataframe):
    """Test the JSSRule."""
    rule = JSSRule()
    params = load_parameters("2023-2024")
    data = {"df": sample_dataframe, "params": params}
    rule(data)
    assert "jss_entitlement" in data["df"].columns


def test_sps_rule(sample_dataframe):
    """Test the SPSRule."""
    rule = SPSRule()
    params = load_parameters("2023-2024")
    data = {"df": sample_dataframe, "params": params}
    rule(data)
    assert "sps_entitlement" in data["df"].columns


def test_slp_rule(sample_dataframe):
    """Test the SLPRule."""
    rule = SLPRule()
    params = load_parameters("2023-2024")
    data = {"df": sample_dataframe, "params": params}
    rule(data)
    assert "slp_entitlement" in data["df"].columns


def test_accommodation_supplement_rule(sample_dataframe):
    """Test the AccommodationSupplementRule."""
    rule = AccommodationSupplementRule()
    params = load_parameters("2023-2024")
    data = {"df": sample_dataframe, "params": params}
    rule(data)
    assert "accommodation_supplement_entitlement" in data["df"].columns


def test_wep_rule(sample_dataframe):
    """Test the WEPRule."""
    rule = WEPRule()
    params = load_parameters("2023-2024")
    data = {"df": sample_dataframe, "params": params}
    rule(data)
    assert "wep_entitlement" in data["df"].columns


def test_bstc_rule(sample_dataframe):
    """Test the BSTCRule."""
    rule = BSTCRule()
    params = load_parameters("2023-2024")
    data = {"df": sample_dataframe, "params": params}
    rule(data)
    assert "bstc_entitlement" in data["df"].columns


def test_ftc_rule(sample_dataframe):
    """Test the FTCRule."""
    rule = FTCRule()
    params = load_parameters("2023-2024")
    data = {"df": sample_dataframe, "params": params}
    rule(data)
    assert "ftc_entitlement" in data["df"].columns


def test_iwtc_rule(sample_dataframe):
    """Test the IWTCRule."""
    rule = IWTCRule()
    params = load_parameters("2023-2024")
    data = {"df": sample_dataframe, "params": params}
    rule(data)
    assert "iwtc_entitlement" in data["df"].columns


def test_mftc_rule(sample_dataframe):
    """Test the MFTCRule."""
    rule = MFTCRule()
    params = load_parameters("2023-2024")
    data = {"df": sample_dataframe, "params": params}
    rule(data)
    assert "mftc_entitlement" in data["df"].columns


def test_disability_allowance_rule(sample_dataframe):
    """Test the DisabilityAllowanceRule."""
    rule = DisabilityAllowanceRule()
    params = load_parameters("2024-2025")
    data = {"df": sample_dataframe, "params": params}
    rule(data)
    assert "disability_allowance_entitlement" in data["df"].columns
