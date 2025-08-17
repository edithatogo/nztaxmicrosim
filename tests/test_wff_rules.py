import pandas as pd
import pytest
from src.wff_rules import (
    GrossUpIncomeRule,
    CalculateMaxEntitlementsRule,
    ApplyCareLogicRule,
    CalculateAbatementRule,
    ApplyCalibrationsRule,
    CalculateFinalEntitlementsRule,
)

@pytest.fixture
def sample_data():
    """Provides a sample DataFrame for testing."""
    return {
        "df": pd.DataFrame({
            "familyinc": [40000, 50000, 60000],
            "sharedcare": [0, 1, 0],
        })
    }

def test_gross_up_income_rule(sample_data):
    rule = GrossUpIncomeRule()
    rule(sample_data)
    df = sample_data["df"]
    assert "wff_income" in df.columns
    assert df["wff_income"].equals(df["familyinc"] * 1.0)

def test_calculate_max_entitlements_rule(sample_data):
    rule = CalculateMaxEntitlementsRule()
    rule(sample_data)
    df = sample_data["df"]
    assert "max_ftc" in df.columns
    assert df["max_ftc"].iloc[0] == 1000
    assert "max_iwc" in df.columns
    assert df["max_iwc"].iloc[0] == 500
    assert "max_bstc" in df.columns
    assert df["max_bstc"].iloc[0] == 300
    assert "max_mftc" in df.columns
    assert df["max_mftc"].iloc[0] == 2000

def test_apply_care_logic_rule(sample_data):
    # First, run the rule that creates 'max_ftc'
    CalculateMaxEntitlementsRule()(sample_data)
    
    rule = ApplyCareLogicRule()
    rule(sample_data)
    df = sample_data["df"]
    
    # Person 0: no shared care, max_ftc should be 1000
    assert df["max_ftc"].iloc[0] == 1000
    # Person 1: shared care, max_ftc should be halved
    assert df["max_ftc"].iloc[1] == 500
    # Person 2: no shared care, max_ftc should be 1000
    assert df["max_ftc"].iloc[2] == 1000

def test_calculate_abatement_rule(sample_data):
    GrossUpIncomeRule()(sample_data)
    rule = CalculateAbatementRule()
    rule(sample_data)
    df = sample_data["df"]
    assert "abatement" in df.columns
    # Income below threshold
    assert df["abatement"].iloc[0] == 0
    # Income above threshold
    expected_abatement = (50000 - 42700) * 0.27
    assert df["abatement"].iloc[1] == expected_abatement

def test_apply_calibrations_rule(sample_data):
    sample_data["df"]["final_wff_entitlement"] = pd.Series([100, 200, 300])
    rule = ApplyCalibrationsRule()
    rule(sample_data)
    df = sample_data["df"]
    assert df["final_wff_entitlement"].equals(pd.Series([100.0, 200.0, 300.0]))

def test_calculate_final_entitlements_rule(sample_data):
    CalculateMaxEntitlementsRule()(sample_data)
    CalculateAbatementRule()(sample_data)
    rule = CalculateFinalEntitlementsRule()
    rule(sample_data)
    df = sample_data["df"]
    assert "FTCcalc" in df.columns
    assert "IWTCcalc" in df.columns
    assert "BSTCcalc" in df.columns
    assert "MFTCcalc" in df.columns
    # Check one calculation
    expected_ftc = max(0, 1000 - ((50000 - 42700) * 0.27))
    assert df["FTCcalc"].iloc[1] == expected_ftc
