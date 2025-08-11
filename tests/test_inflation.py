import pandas as pd
import pytest
from unittest.mock import patch
from src.inflation import adjust_for_inflation, get_cpi_data

@pytest.fixture
def sample_data():
    """Provides a sample DataFrame for testing."""
    data = {
        "year": [1990, 1990, 1991],
        "income": [20000, 50000, 22000],
        "expenditure": [10000, 25000, 11000],
    }
    return pd.DataFrame(data)

@pytest.fixture
def mock_cpi_data():
    """A mock CPI data dictionary."""
    return {
        1990: 50.0,
        2000: 75.0,
        2023: 100.0,
    }

@patch("src.inflation.get_cpi_data")
def test_adjust_for_inflation_basic(mock_get_cpi, sample_data, mock_cpi_data):
    """Test a basic inflation adjustment."""
    mock_get_cpi.return_value = mock_cpi_data

    base_year = 2023
    target_year = 1990
    columns_to_adjust = ["income", "expenditure"]

    adjusted_df = adjust_for_inflation(
        sample_data, base_year, target_year, columns_to_adjust
    )

    # Expected adjustment factor: 100.0 / 50.0 = 2.0
    expected_income = sample_data["income"] * 2.0
    pd.testing.assert_series_equal(adjusted_df["income"], expected_income)

    expected_expenditure = sample_data["expenditure"] * 2.0
    pd.testing.assert_series_equal(adjusted_df["expenditure"], expected_expenditure)

    # Ensure other columns are untouched
    assert "year" in adjusted_df.columns
    pd.testing.assert_series_equal(adjusted_df["year"], sample_data["year"])

@patch("src.inflation.get_cpi_data")
def test_adjust_for_inflation_missing_column(mock_get_cpi, sample_data, mock_cpi_data):
    """Test that a missing column is handled gracefully."""
    mock_get_cpi.return_value = mock_cpi_data

    base_year = 2023
    target_year = 1990
    columns_to_adjust = ["income", "non_existent_column"]

    # This should not raise an error
    adjusted_df = adjust_for_inflation(
        sample_data, base_year, target_year, columns_to_adjust
    )

    # Check that the existing column was still adjusted
    expected_income = sample_data["income"] * 2.0
    pd.testing.assert_series_equal(adjusted_df["income"], expected_income)

@patch("src.inflation.get_cpi_data")
def test_adjust_for_inflation_missing_year(mock_get_cpi, sample_data, mock_cpi_data):
    """Test that a ValueError is raised for a missing year in CPI data."""
    mock_get_cpi.return_value = mock_cpi_data

    with pytest.raises(ValueError, match="CPI data not available for base year: 2025"):
        adjust_for_inflation(sample_data, 2025, 1990, ["income"])

    with pytest.raises(ValueError, match="CPI data not available for target year: 1980"):
        adjust_for_inflation(sample_data, 2023, 1980, ["income"])

# We don't test get_cpi_data directly hitting the API in a unit test,
# but we could add an integration test for it if needed.
# For now, we assume the wbdata library works as expected.
# The mocking in the tests above validates the logic that USES the data.
