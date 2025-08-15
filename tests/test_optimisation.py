<<<<<<< HEAD
import pandas as pd
import pytest

from src.microsim import load_parameters
from src.optimisation import run_parameter_scan, run_policy_optimisation

=======
import pytest
import pandas as pd
from src.optimisation import run_parameter_scan, run_policy_optimisation
from src.parameters import Parameters
from src.microsim import load_parameters
>>>>>>> origin/update-a-bunch-of-stuff-5

@pytest.fixture
def sample_df():
    """A sample DataFrame for testing."""
    return pd.DataFrame({"taxable_income": [50000]})

<<<<<<< HEAD

@pytest.fixture
def sample_metrics():
    """Sample metric functions."""
    return {"total_tax": lambda df: df["tax_liability"].sum(), "person_count": lambda df: len(df)}

=======
@pytest.fixture
def sample_metrics():
    """Sample metric functions."""
    return {
        "total_tax": lambda df: df["tax_liability"].sum(),
        "person_count": lambda df: len(df)
    }
>>>>>>> origin/update-a-bunch-of-stuff-5

@pytest.fixture
def valid_scan_config():
    """A valid scan configuration for testing."""
    return {
        "scenarios": [
<<<<<<< HEAD
            {"id": "base_case", "parameters": {}},
            {"id": "scenario_1", "parameters": {"tax_brackets.rates": [0.10, 0.20, 0.30, 0.40, 0.50], "ietc.ent": 600}},
        ]
    }


=======
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

>>>>>>> origin/update-a-bunch-of-stuff-5
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

<<<<<<< HEAD

=======
>>>>>>> origin/update-a-bunch-of-stuff-5
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

<<<<<<< HEAD

=======
>>>>>>> origin/update-a-bunch-of-stuff-5
@pytest.fixture
def valid_opt_config():
    """A valid optimisation configuration for testing."""
    return {
<<<<<<< HEAD
        "objective": {"name": "total_tax", "direction": "maximize"},
        "n_trials": 1,  # Run only one trial for testing
        "search_space": [
            {"name": "top_tax_rate", "path": "tax_brackets.rates.4", "type": "float", "low": 0.4, "high": 0.5},
            {"name": "ietc_entitlement", "path": "ietc.ent", "type": "int", "low": 500, "high": 700},
        ],
    }


=======
        "objective": {
            "name": "total_tax",
            "direction": "maximize"
        },
        "n_trials": 1, # Run only one trial for testing
        "search_space": [
            {
                "name": "top_tax_rate",
                "path": "tax_brackets.rates.4",
                "type": "float",
                "low": 0.4,
                "high": 0.5
            },
            {
                "name": "ietc_entitlement",
                "path": "ietc.ent",
                "type": "int",
                "low": 500,
                "high": 700
            }
        ]
    }

>>>>>>> origin/update-a-bunch-of-stuff-5
def test_run_policy_optimisation(sample_df, valid_opt_config, sample_metrics, monkeypatch):
    """Test the main logic of the policy optimisation runner."""

    # Mock the study and trial objects to test the objective function in isolation
    class MockTrial:
        def __init__(self):
            self.user_attrs = {}
<<<<<<< HEAD

        def suggest_float(self, name, low, high):
            return 0.45  # Return a fixed value for predictability

        def suggest_int(self, name, low, high):
            return 650

=======
        def suggest_float(self, name, low, high):
            return 0.45  # Return a fixed value for predictability
        def suggest_int(self, name, low, high):
            return 650
>>>>>>> origin/update-a-bunch-of-stuff-5
        def set_user_attr(self, key, value):
            self.user_attrs[key] = value

    class MockStudy:
        def optimize(self, objective, n_trials):
            # Call the objective function once with a mock trial
            trial = MockTrial()
            result = objective(trial)
            self.objective_result = result
            self.trial = trial

        @property
        def best_params(self):
            return {"top_tax_rate": 0.45, "ietc_entitlement": 650}

    mock_study_instance = MockStudy()

    def mock_create_study(direction):
        assert direction == "maximize"
        return mock_study_instance

    monkeypatch.setattr("src.optimisation.optuna.create_study", mock_create_study)

    # Mock the simulation to check that parameters are applied correctly
    modified_params_storage = []
<<<<<<< HEAD

=======
>>>>>>> origin/update-a-bunch-of-stuff-5
    def mock_simulation(df, params):
        modified_params_storage.append(params)
        return pd.DataFrame({"tax_liability": [2000]})

    monkeypatch.setattr("src.optimisation._run_static_simulation", mock_simulation)

<<<<<<< HEAD
    _ = run_policy_optimisation(sample_df, "2023-2024", valid_opt_config, sample_metrics)
=======
    study = run_policy_optimisation(sample_df, "2023-2024", valid_opt_config, sample_metrics)
>>>>>>> origin/update-a-bunch-of-stuff-5

    # 1. Check that the objective function returned the correct value
    assert mock_study_instance.objective_result == 2000

    # 2. Check that the parameters were modified as suggested by the mock trial
    assert len(modified_params_storage) == 1
    modified_params = modified_params_storage[0]
    assert modified_params.tax_brackets.rates[4] == 0.45
    assert modified_params.ietc.ent == 650

    # 3. Check that all metrics were stored in user_attrs
    stored_metrics = mock_study_instance.trial.user_attrs["metrics"]
    assert stored_metrics["total_tax"] == 2000
    assert stored_metrics["person_count"] == 1
