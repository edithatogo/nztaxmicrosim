"""Tests for the dynamic simulation framework."""

import pandas as pd
import pytest

from src.dynamic_simulation import run_dynamic_simulation
from src.microsim import load_parameters, taxit


@pytest.fixture
def sample_dataframe():
    """A sample dataframe for testing the simulation functions."""
    data = {
        "taxable_income": [30000, 60000],
        "familyinc": [70000, 70000],
        "FTCwgt": [2, 2],
        "IWTCwgt": [2, 2],
        "BSTC0wgt": [0, 0],
        "BSTC01wgt": [0, 0],
        "BSTC1wgt": [1, 1],
        "MFTCwgt": [0, 0],
        "iwtc_elig": [12, 12],
        "pplcnt": [4, 4],
        "MFTC_total": [0, 0],
        "MFTC_elig": [0, 0],
        "sharedcare": [0, 0],
        "sharecareFTCwgt": [0, 0],
        "sharecareBSTC0wgt": [0, 0],
        "sharecareBSTC01wgt": [0, 0],
        "sharecareBSTC1wgt": [0, 0],
        "iwtc": [1, 1],
        "selfempind": [0, 0],
        "maxkiddays": [365, 365],
        "maxkiddaysbstc": [365, 365],
    }
    return pd.DataFrame(data)


def test_year_to_year_progression(sample_dataframe):
    years = ["2022-2023", "2023-2024"]

    results = run_dynamic_simulation(sample_dataframe, years)

    params1 = load_parameters("2022-2023")
    expected1 = [taxit(i, params1.tax_brackets) for i in sample_dataframe["taxable_income"]]
    assert results["2022-2023"]["tax_liability"].tolist() == expected1
    assert "FTCcalc" in results["2022-2023"].columns

    params2 = load_parameters("2023-2024")
    expected2 = [taxit(i, params2.tax_brackets) for i in sample_dataframe["taxable_income"]]
    assert results["2023-2024"]["tax_liability"].tolist() == expected2
    assert "FTCcalc" in results["2023-2024"].columns


def test_labour_response_applied(sample_dataframe):
    years = ["2022-2023", "2023-2024"]

    # This mock function simulates a behavioural response by increasing income.
    # It ignores the other parameters to keep the test simple and focused.
    def mock_behavioural_func(df_before, df_after, emtr_calculator_before, emtr_calculator_after, elasticity_params):
        updated = df_after.copy()
        updated["taxable_income"] *= 1.1
        return updated

    results = run_dynamic_simulation(
        sample_dataframe,
        years,
        use_behavioural_response=True,
        # Provide dummy elasticity params as they are required by the function signature
        elasticity_params={"dummy": 0.1},
        behavioural_func=mock_behavioural_func,
    )

    # In the first year, the income is increased by 10%
    params1 = load_parameters("2022-2023")
    income1 = sample_dataframe["taxable_income"].iloc[0] * 1.1
    expected1 = taxit(income1, params1.tax_brackets)
    assert results["2022-2023"]["tax_liability"].iloc[0] == expected1

    # In the second year, the income from the end of the first year (already increased)
    # is increased by another 10%
    params2 = load_parameters("2023-2024")
    income2 = income1 * 1.1
    expected2 = taxit(income2, params2.tax_brackets)
    assert results["2023-2024"]["tax_liability"].iloc[0] == expected2
