from unittest.mock import patch

import pandas as pd
import pytest

from src.demographic_modelling import age_population_forward


@pytest.fixture
def sample_population():
    """Provides a sample population DataFrame for testing."""
    data = {
        "person_id": [1, 2, 3],
        "family_id": [1, 1, 2],
        "age": [30, 32, 25],
        "sex": ["Female", "Male", "Female"],
        "income": [50000, 70000, 40000],
    }
    return pd.DataFrame(data)


@pytest.fixture
def mock_fertility_data():
    """Provides mock fertility data for a specific year."""
    return {
        "1990": {
            "15-19": 0.0,
            "20-24": 0.0,
            "25-29": 0.0,
            "30-34": 1000.0,  # 100% chance for a 30-year-old
            "35-39": 0.0,
            "40-44": 0.0,
        },
        "1991": {"15-19": 0.0, "20-24": 0.0, "25-29": 0.0, "30-34": 0.0, "35-39": 0.0, "40-44": 0.0},
    }


@patch("src.demographic_modelling.get_fertility_data")
def test_age_increment(mock_get_fertility, sample_population, mock_fertility_data):
    """Test that everyone's age is incremented by 1."""
    mock_get_fertility.return_value = mock_fertility_data

    original_ages = sample_population["age"].copy()
    aged_df = age_population_forward(sample_population, 1991)  # Use a year with 0 fertility

    expected_ages = original_ages + 1
    # We only check the original population, not the babies
    pd.testing.assert_series_equal(aged_df["age"].iloc[: len(original_ages)], expected_ages, check_names=False)


@patch("src.demographic_modelling.get_fertility_data")
def test_birth_simulation_guaranteed(mock_get_fertility, sample_population, mock_fertility_data):
    """Test that a birth occurs when the fertility rate is 1.0."""
    mock_get_fertility.return_value = mock_fertility_data

    # In our mock data for 1990, a 30-year-old woman has a 100% chance of giving birth.
    aged_df = age_population_forward(sample_population, 1990)

    # Original population was 3, so we expect 1 new baby.
    assert len(aged_df) == 4

    # Check the details of the new baby
    baby = aged_df.iloc[-1]
    assert baby["age"] == 0
    assert baby["family_id"] == 1  # Should be the family of the 30-year-old mother
    assert baby["income"] == 0


@patch("src.demographic_modelling.get_fertility_data")
def test_birth_simulation_zero(mock_get_fertility, sample_population, mock_fertility_data):
    """Test that no births occur when fertility rates are 0."""
    mock_get_fertility.return_value = mock_fertility_data

    # In our mock data for 1991, all fertility rates are 0.
    aged_df = age_population_forward(sample_population, 1991)

    # No new births should occur.
    assert len(aged_df) == 3


@patch("src.demographic_modelling.get_fertility_data")
def test_missing_fertility_data_for_year(mock_get_fertility, sample_population):
    """Test that the function runs without error if the year is missing from data."""
    mock_get_fertility.return_value = {"2000": {"30-34": 50.0}}  # Data for a different year

    # Should run without error and just age the population.
    aged_df = age_population_forward(sample_population, 1995)

    assert len(aged_df) == 3
    assert aged_df["age"].iloc[0] == 31
