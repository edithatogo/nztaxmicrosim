"""
Unit tests for the microsimulation tax functions.

This module contains tests for the functions defined in `src/microsim.py`,
ensuring their correctness and adherence to the original SAS model logic.
"""

import inspect
from pathlib import Path
import sqlite3
import json

import pytest

from src.microsim import (
    calctax,
    calculate_net_weekly_income,
    load_parameters,
    simrwt,
    supstd,
    taxit,
)
from src.parameters import RWTParams, TaxBracketParams, Parameters


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """Creates a temporary SQLite database with test parameter data."""
    db_path = tmp_path / "test_parameters.db"

    # Monkeypatch the database path in the source module
    monkeypatch.setattr("src.microsim.DB_PATH", str(db_path))

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE policy_parameters (
        year INTEGER,
        policy_key TEXT,
        parameters TEXT,
        PRIMARY KEY (year, policy_key)
    )
    """)

    # Insert data for year 2020
    params_2020 = {
        "tax_brackets": {"rates": [0.1, 0.2], "thresholds": [10000]},
        "ietc": None, # Policy doesn't exist
        "wff": {"ftc1": 100, "ftc2": 50, "iwtc1": 30, "iwtc2": 10, "bstc": 20, "mftc": 500, "abatethresh1": 10000, "abatethresh2": 20000, "abaterate1": 0.1, "abaterate2": 0.2, "bstcthresh": 5000, "bstcabate": 0.1}
    }
    for key, value in params_2020.items():
        cursor.execute(
            "INSERT INTO policy_parameters (year, policy_key, parameters) VALUES (?, ?, ?)",
            (2020, key, json.dumps(value) if value is not None else None)
        )

    # Insert data for year 2021 (with invalid JSON for one key)
    cursor.execute(
        "INSERT INTO policy_parameters (year, policy_key, parameters) VALUES (?, ?, ?)",
        (2021, "tax_brackets", '{"rates": "not-a-list", "thresholds": []}')
    )

    conn.commit()
    conn.close()

    return db_path


def test_load_parameters_from_db(test_db):
    """Test that parameters are correctly loaded from the SQLite database."""
    params = load_parameters("2020")
    assert isinstance(params, Parameters)
    assert params.tax_brackets.rates == [0.1, 0.2]
    assert params.ietc is None
    assert params.wff.ftc1 == 100

def test_load_parameters_year_not_found(test_db):
    """Test that a ValueError is raised for a year not in the database."""
    with pytest.raises(ValueError, match="No parameters found for year 1999"):
        load_parameters("1999")

def test_load_parameters_invalid_json_in_db(test_db):
    """Test that a validation error is raised for malformed JSON in the db."""
    with pytest.raises(ValueError, match="Parameter validation for year 2021 failed"):
        load_parameters("2021")


def test_taxit():
    """
    Tests the taxit function with various income scenarios and tax brackets.
    """
    # Rates and thresholds for the 2023 tax year
    rates = [0.105, 0.175, 0.30, 0.33, 0.39]
    thresholds = [14000.0, 48000.0, 70000.0, 180000.0]
    params = TaxBracketParams(rates=rates, thresholds=thresholds)

    # Test case 1: Income within the first bracket
    params = TaxBracketParams(rates=rates, thresholds=thresholds)

    assert taxit(10000, params) == 1050

    # Test case 2: Income in the second bracket
    assert taxit(20000, params) == 14000 * 0.105 + (20000 - 14000) * 0.175

    # Test case 3: Income in the third bracket
    assert taxit(60000, params) == (14000 * 0.105) + ((48000 - 14000) * 0.175) + ((60000 - 48000) * 0.30)

    # Test case 4: Income in the fourth bracket
    assert taxit(100000, params) == (14000 * 0.105) + ((48000 - 14000) * 0.175) + ((70000 - 48000) * 0.30) + (
        (100000 - 70000) * 0.33
    )

    # Test case 5: Income in the fifth bracket
    assert taxit(200000, params) == (14000 * 0.105) + ((48000 - 14000) * 0.175) + ((70000 - 48000) * 0.30) + (
        (180000 - 70000) * 0.33
    ) + ((200000 - 180000) * 0.39)

    # Test case 6: Zero income
    assert taxit(0, params) == 0

    # Test case 7: Negative income
    assert taxit(-1000, params) == 0


def test_calctax():
    """
    Tests the calctax function for split-year tax calculations.
    """
    # Rates and thresholds for the 2023 tax year
    params1 = TaxBracketParams(rates=[0.105, 0.175, 0.30, 0.33, 0.39], thresholds=[14000, 48000, 70000, 180000])

    # Rates and thresholds for the 2024 tax year
    params2 = TaxBracketParams(rates=[0.105, 0.175, 0.30, 0.33, 0.39], thresholds=[14000, 48000, 70000, 180000])

    # Test case 1: Split year with same rates and thresholds
    assert calctax(60000, 6, params1, params1) == taxit(60000, params1)

    # Test case 2: Split year with different rates and thresholds
    tax1 = taxit(60000, params1)
    tax2 = taxit(60000, params2)
    expected_tax = tax1 * 0.5 + tax2 * 0.5
    assert calctax(60000, 6, params1, params2) == expected_tax


def test_calculate_net_weekly_income():
    """
    Tests the calculate_net_weekly_income function.
    """
    # Rates and thresholds for the 2023 tax year
    rates = [0.105, 0.175, 0.30, 0.33, 0.39]
    thresholds = [14000.0, 48000.0, 70000.0, 180000.0]
    params = TaxBracketParams(rates=rates, thresholds=thresholds)
    eprt = 0.0146

    # Test case 1
    incvar = 1000
    annearn = incvar * 52
    temptax = taxit(annearn, params)
    expected_net = int(100 * (annearn * (1 - eprt) - temptax) / 52) / 100
    assert calculate_net_weekly_income(incvar, eprt, params) == expected_net


def test_simrwt():
    """Tests the simrwt function for Resident Withholding Tax calculation."""
    # Test case 1: Basic RWT calculation
    assert simrwt(1000, 0.105) == 105

    # Test case 2: Zero interest
    assert simrwt(0, 0.105) == 0

    # Test case 3: Negative interest
    assert simrwt(-1000, 0.105) == 0

    # Test case 4: Zero rate
    assert simrwt(1000, 0) == 0

    # Test case 5: Invalid rate
    with pytest.raises(ValueError):
        simrwt(1000, 1.1)
    with pytest.raises(ValueError):
        simrwt(1000, -0.1)


def test_supstd():
    """
    Tests the supstd function for standard superannuation calculation.
    """
    # Base year parameters
    base_year_awe = 1462.81
    base_year_ep_rate = 0.0153
    tax_params_base = load_parameters("2022").tax_brackets

    # Simulation year parameters
    cpi_factors = [1.05, 1.04, 1.03, 1.02]
    awe = [1546.57, 1630.11, 1701.45, 1763.49]
    ep = [0.016, 0.016, 0.016, 0.016]
    fl = [0.66, 0.66, 0.66, 0.66]
    tax_params = [
        load_parameters("2022").tax_brackets,
        load_parameters("2023").tax_brackets,
        load_parameters("2024").tax_brackets,
            load_parameters("2024").tax_brackets,  # Use 2024 again as 2025 is not in db
    ]

    # Expected results
    expected_std22 = base_year_awe * 0.66 * 2
    expected_stdnet22 = calculate_net_weekly_income(
        gross_weekly_income=expected_std22 / 2,
        acc_earners_premium_rate=base_year_ep_rate,
        tax_params=tax_params_base,
    )

    expected_std = []
    expected_stdnet = []
    std_prev = expected_std22
    for i in range(4):
        std = max(awe[i] * fl[i] * 2, std_prev * cpi_factors[i])
        stdnet = calculate_net_weekly_income(
            gross_weekly_income=std / 2, acc_earners_premium_rate=ep[i], tax_params=tax_params[i]
        )
        expected_std.append(std)
        expected_stdnet.append(stdnet)
        std_prev = std

    # Run the function
    results = supstd(
        cpi_factors,
        awe,
        ep,
        fl,
        tax_params,
        base_year_awe,
        base_year_ep_rate,
        tax_params_base,
    )

    # Assertions
    assert results["std22"] == expected_std22
    assert results["stdnet22"] == expected_stdnet22
    assert results["std"] == expected_std[0]
    assert results["stdnet"] == expected_stdnet[0]
    assert results["std1"] == expected_std[1]
    assert results["stdnet1"] == expected_stdnet[1]
    assert results["std2"] == expected_std[2]
    assert results["stdnet2"] == expected_stdnet[2]
    assert results["std3"] == expected_std[3]
    assert results["stdnet3"] == expected_stdnet[3]