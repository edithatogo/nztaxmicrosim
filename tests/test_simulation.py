import pandas as pd
import pytest

from src.simulation import run_simulation


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


def test_run_simulation_static_mode(sample_dataframe):
    """Test the run_simulation function in static mode."""
    result = run_simulation(sample_dataframe.copy(), mode="static", year="2023-2024")

    assert isinstance(result, pd.DataFrame)
    assert "tax_liability" in result.columns
    assert "FTCcalc" in result.columns


def test_run_simulation_dynamic_mode(sample_dataframe):
    """Test the run_simulation function in dynamic mode."""
    years = ["2022-2023", "2023-2024"]
    results = run_simulation(sample_dataframe.copy(), mode="dynamic", year=years)

    assert isinstance(results, dict)
    assert "2022-2023" in results
    assert "2023-2024" in results
    assert "tax_liability" in results["2022-2023"].columns
    assert "FTCcalc" in results["2022-2023"].columns


def test_run_simulation_invalid_mode(sample_dataframe):
    """Test that run_simulation raises an error for an invalid mode."""
    with pytest.raises(ValueError):
        run_simulation(sample_dataframe, mode="invalid_mode", year="2023-2024")


def test_run_simulation_static_mode_invalid_year(sample_dataframe):
    """Test that run_simulation raises an error for an invalid year in static mode."""
    with pytest.raises(ValueError):
        run_simulation(sample_dataframe, mode="static", year=["2022-2023", "2023-2024"])


def test_run_simulation_dynamic_mode_invalid_year(sample_dataframe):
    """Test that run_simulation raises an error for an invalid year in dynamic mode."""
    with pytest.raises(ValueError):
        run_simulation(sample_dataframe, mode="dynamic", year="2023-2024")
