import pytest
import pandas as pd
from src.optimisation import run_parameter_scan
from src.parameters import Parameters
from src.microsim import load_parameters

@pytest.fixture
def sample_df():
    """A sample DataFrame for testing."""
    return pd.DataFrame({"taxable_income": [50000]})

@pytest.fixture
def sample_metrics():
    """Sample metric functions."""
    return {
        "total_tax": lambda df: df["tax_liability"].sum(),
        "person_count": lambda df: len(df)
    }

@pytest.fixture
def valid_scan_config():
    """A valid scan configuration for testing."""
    return {
        "scenarios": [
            {
                "id": "base_case",
                "parameters": {}
            },
            {
                "id": "scenario_1",
                "parameters": {
                    "tax_brackets.rates": [0.10, 0.20, 0.30, 0.40, 0.50],
                    "ietc.ent": 600
                }
            }
        ]
    }

def test_run_parameter_scan_happy_path(sample_df, valid_scan_config, sample_metrics, monkeypatch):
    """Test that the parameter scan runs successfully with a valid config."""

    # Mock the simulation function to avoid running a full simulation
    def mock_simulation(df, params):
        # The mock just adds a dummy tax_liability column
        result_df = df.copy()
        result_df["tax_liability"] = 1000  # A constant value for simplicity
        return result_df

    monkeypatch.setattr("src.optimisation._run_static_simulation", mock_simulation)

    results = run_parameter_scan(sample_df, "2023-2024", valid_scan_config, sample_metrics)

    assert isinstance(results, pd.DataFrame)
    assert len(results) == 2
    assert list(results.columns) == ["scenario_id", "total_tax", "person_count"]
    assert results["scenario_id"].tolist() == ["base_case", "scenario_1"]
    assert results["total_tax"].tolist() == [1000, 1000]
    assert results["person_count"].tolist() == [1, 1]

def test_parameter_modification(sample_df, valid_scan_config, sample_metrics, monkeypatch):
    """Test that parameters are correctly modified for each scenario."""

    original_params = load_parameters("2023-2024")
    modified_params_storage = []

    def mock_simulation_with_capture(df, params):
        modified_params_storage.append(params)
        return pd.DataFrame({"tax_liability": [0]})

    monkeypatch.setattr("src.optimisation._run_static_simulation", mock_simulation_with_capture)

    run_parameter_scan(sample_df, "2023-2024", valid_scan_config, sample_metrics)

    assert len(modified_params_storage) == 2

    # Check base case (should be unchanged)
    assert modified_params_storage[0].tax_brackets.rates == original_params.tax_brackets.rates
    assert modified_params_storage[0].ietc.ent == original_params.ietc.ent

    # Check scenario 1
    assert modified_params_storage[1].tax_brackets.rates == [0.10, 0.20, 0.30, 0.40, 0.50]
    assert modified_params_storage[1].ietc.ent == 600

    # Ensure the original parameters were not modified (i.e., a deep copy was made)
    assert original_params.ietc.ent != 600


def test_invalid_config_raises_errors(sample_df, sample_metrics):
    """Test that malformed configurations raise appropriate errors."""

    # Missing 'scenarios' key
    with pytest.raises(ValueError, match="must contain a 'scenarios' key"):
        run_parameter_scan(sample_df, "2023-2024", {}, sample_metrics)

    # Scenario without 'id'
    with pytest.raises(ValueError, match="must have 'id' and 'parameters' keys"):
        config = {"scenarios": [{"parameters": {}}]}
        run_parameter_scan(sample_df, "2023-2024", config, sample_metrics)

    # Scenario with invalid parameter path
    with pytest.raises(AttributeError, match="Invalid parameter path"):
        config = {"scenarios": [{"id": "s1", "parameters": {"non_existent.param": 1}}]}
        run_parameter_scan(sample_df, "2023-2024", config, sample_metrics)
