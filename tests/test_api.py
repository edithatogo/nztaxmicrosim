import os

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


@pytest.fixture(scope="module")
def test_data_dir():
    """Create a directory for test uploads."""
    test_dir = "tests/test_api_uploads"
    os.makedirs(test_dir, exist_ok=True)
    yield test_dir
    # Clean up the test directory and its contents
    for f in os.listdir(test_dir):
        os.remove(os.path.join(test_dir, f))
    os.rmdir(test_dir)


@pytest.fixture(scope="module")
def sample_csv_file(test_data_dir):
    """Create a sample CSV file for uploading that matches the expected schema."""
    filepath = os.path.join(test_data_dir, "sample.csv")
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
    }
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False)
    return filepath


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the NZ Tax Microsimulation Model API"}


def test_upload_data(sample_csv_file):
    with open(sample_csv_file, "rb") as f:
        response = client.post("/data/upload", files={"file": ("sample.csv", f, "text/csv")})
    assert response.status_code == 200
    json_response = response.json()
    assert "dataset_id" in json_response
    assert json_response["filename"] == "sample.csv"


def test_get_data_metadata(sample_csv_file):
    # First, upload a file to get a dataset_id
    with open(sample_csv_file, "rb") as f:
        upload_response = client.post("/data/upload", files={"file": ("sample.csv", f, "text/csv")})
    dataset_id = upload_response.json()["dataset_id"]

    # Now, get the metadata
    response = client.get(f"/data/{dataset_id}")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["dataset_id"] == dataset_id
    assert "size_bytes" in json_response
    assert "created_at" in json_response


def test_get_nonexistent_metadata():
    response = client.get("/data/nonexistent-id")
    assert response.status_code == 404


def test_run_static_simulation_default_pop():
    request_body = {
        "year": "2023-2024",
        "parameter_overrides": {
            "tax_brackets.rates.4": 0.45  # Change top tax rate
        },
    }
    response = client.post("/simulation/static", json=request_body)
    assert response.status_code == 200
    json_response = response.json()
    assert "total_tax_liability" in json_response
    assert "total_wff_paid" in json_response
    assert json_response["num_records"] > 0


def test_run_static_simulation_custom_pop(sample_csv_file):
    # First, upload a file to get a dataset_id
    with open(sample_csv_file, "rb") as f:
        upload_response = client.post("/data/upload", files={"file": ("sample.csv", f, "text/csv")})
    dataset_id = upload_response.json()["dataset_id"]

    request_body = {"year": "2023-2024", "dataset_id": dataset_id, "parameter_overrides": {}}
    response = client.post("/simulation/static", json=request_body)
    assert response.status_code == 200
    json_response = response.json()
    assert "total_tax_liability" in json_response
    assert "total_wff_paid" in json_response
    assert json_response["num_records"] == 2


def test_run_static_simulation_bad_dataset_id():
    request_body = {"year": "2023-2024", "dataset_id": "nonexistent-id"}
    response = client.post("/simulation/static", json=request_body)
    assert response.status_code == 404


# Testing the async optimisation endpoint is more complex and requires
# mocking Celery. For this exercise, we will assume the manual tests
# during development were sufficient. A production system would need
# proper mocking of celery.delay and AsyncResult.
