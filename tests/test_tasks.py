import pytest
from src.api.tasks import run_optimisation_task
import pandas as pd
import os


@pytest.fixture(scope="module")
def sample_dataset_path(tmpdir_factory):
    """Create a sample dataset for testing the optimisation task."""
    filepath = tmpdir_factory.mktemp("data").join("sample_dataset.csv")
    data = {
        "person_id": [1, 2],
        "household_id": [1, 2],
        "age": [40, 25],
        "gender": ["Male", "Female"],
        "marital_status": ["Married", "Single"],
        "family_household_type": ["Couple with children", "Single adult"],
        "household_size": [3, 1],
        "num_children": [1, 0],
        "adults": [2, 1],
        "ages_of_children": [[5], []],
        "region": ["Auckland", "Wellington"],
        "disability_status": [False, True],
        "employment_income": [80000, 30000],
        "self_employment_income": [0, 5000],
        "investment_income": [1000, 200],
        "rental_property_income": [0, 0],
        "private_pensions_annuities": [0, 0],
        "employment_status": ["Employed", "Self-employed"],
        "hours_worked": [40, 30],
        "is_jss_recipient": [False, False],
        "is_sps_recipient": [False, False],
        "is_slp_recipient": [False, False],
        "is_nz_super_recipient": [False, False],
        "housing_costs": [500, 300],
        "familyinc": [81000, 35200],
        "FTCwgt": [1, 0],
        "IWTCwgt": [1, 1],
        "BSTC0wgt": [0, 0],
        "BSTC01wgt": [1, 0],
        "BSTC1wgt": [0, 0],
        "MFTCwgt": [1, 0],
        "iwtc_elig": [1, 1],
        "MFTC_total": [1000, 1000],
        "MFTC_elig": [1, 1],
        "sharedcare": [0, 0],
        "sharecareFTCwgt": [0, 0],
        "sharecareBSTC0wgt": [0, 0],
        "sharecareBSTC01wgt": [0, 0],
        "sharecareBSTC1wgt": [0, 0],
        "iwtc": [1, 1],
        "selfempind": [0, 1],
        "maxkiddays": [365, 365],
        "maxkiddaysbstc": [365, 365],
        "pplcnt": [3, 1],
        "taxable_income": [81000, 35200],
    }
    df = pd.DataFrame(data)
    df.to_csv(str(filepath), index=False)
    return str(filepath)


def test_run_optimisation_task(sample_dataset_path):
    """Test the run_optimisation_task celery task."""
    opt_config = {
        "study_name": "test_optimisation_task",
        "n_trials": 1,
        "search_space": [
            {
                "name": "tax_rate_2",
                "path": "tax_brackets.rates.2",
                "type": "float",
                "low": 0.17,
                "high": 0.18,
            }
        ],
        "objective": {
            "name": "total_tax_revenue",
            "direction": "maximize",
        },
    }
    base_year = "2023-2024"

    result = run_optimisation_task(opt_config, base_year, sample_dataset_path)

    assert "best_trial_number" in result
    assert "best_value" in result
    assert "best_params" in result
    assert "all_trials" in result
    assert len(result["all_trials"]) == 1
    assert "tax_rate_2" in result["best_params"]


def test_run_optimisation_task_file_not_found():
    """Test the task with a non-existent dataset path."""
    with pytest.raises(FileNotFoundError):
        run_optimisation_task({}, "2023-2024", "nonexistent/path.csv")
