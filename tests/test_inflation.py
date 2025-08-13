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

def test_adjust_for_inflation_zero_cpi(sample_data, mock_cpi_data):
    """Test that a ValueError is raised if the target year CPI is zero."""
    mock_cpi_data[1990] = 0.0
    with patch("src.inflation.get_cpi_data", return_value=mock_cpi_data):
        with pytest.raises(ValueError, match="CPI for target year 1990 is zero"):
            adjust_for_inflation(sample_data, 2023, 1990, ["income"])

def test_adjust_for_inflation_empty_cpi(sample_data):
    """Test that the function returns the original dataframe if CPI data is empty."""
    with patch("src.inflation.get_cpi_data", return_value={}):
        adjusted_df = adjust_for_inflation(sample_data, 2023, 1990, ["income"])
        pd.testing.assert_frame_equal(adjusted_df, sample_data)

def test_get_cpi_data_from_api(monkeypatch, tmp_path):
    """Test fetching CPI data from the API and creating a cache file."""
    # 1. Setup mocks
    # Mock the wbdata API call
    mock_api_df = pd.DataFrame({
        'cpi': [98.5, 99.2],
    }, index=pd.MultiIndex.from_tuples([('New Zealand', '2021'), ('New Zealand', '2022')], names=['country', 'date']))

    mock_get_dataframe = lambda *args, **kwargs: mock_api_df
    monkeypatch.setattr("src.inflation.wbdata.get_dataframe", mock_get_dataframe)

    # Use a temporary directory for the cache
    monkeypatch.setattr("src.inflation.CPI_CACHE_FILE", tmp_path / "cpi_data.json")
    cache_file = tmp_path / "cpi_data.json"

    # 2. Run the function
    # Ensure no cache exists initially
    assert not cache_file.exists()
    cpi_data = get_cpi_data()

    # 3. Assert results
    assert cpi_data == {2021: 98.5, 2022: 99.2}
    assert cache_file.exists()
    with open(cache_file, "r") as f:
        assert '{"2021": 98.5, "2022": 99.2}' in f.read()

def test_get_cpi_data_from_cache(monkeypatch, tmp_path):
    """Test reading CPI data from an existing cache file."""
    # 1. Setup mocks
    # This mock will fail the test if the API is called
    def mock_api_call_fail(*args, **kwargs):
        pytest.fail("API should not be called when cache exists.")
    monkeypatch.setattr("src.inflation.wbdata.get_dataframe", mock_api_call_fail)

    # Use a temporary directory and create a dummy cache file
    cache_file = tmp_path / "cpi_data.json"
    with open(cache_file, "w") as f:
        f.write('{"2020": 95.1, "2021": 98.5}')
    monkeypatch.setattr("src.inflation.CPI_CACHE_FILE", cache_file)

    # 2. Run the function
    cpi_data = get_cpi_data()

    # 3. Assert results
    assert cpi_data == {2020: 95.1, 2021: 98.5}

def test_get_cpi_data_api_failure(monkeypatch, tmp_path):
    """Test that an empty dict is returned if the API call fails."""
    # 1. Setup mocks
    def mock_api_call_fail(*args, **kwargs):
        raise ConnectionError("API is down")
    monkeypatch.setattr("src.inflation.wbdata.get_dataframe", mock_api_call_fail)

    # Use a temporary directory for the cache
    monkeypatch.setattr("src.inflation.CPI_CACHE_FILE", tmp_path / "cpi_data.json")

    # 2. Run the function
    cpi_data = get_cpi_data()

    # 3. Assert results
    assert cpi_data == {}

