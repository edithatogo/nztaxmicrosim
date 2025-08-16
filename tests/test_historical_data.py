"""Tests for the historical_data module."""

from src.historical_data import load_historical_data


def test_load_historical_data():
    """Tests that the historical data can be loaded."""
    data = load_historical_data()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "year" in data[0]
    assert "description" in data[0]
    assert "rates" in data[0]


# The test for get_historical_parameters is now obsolete since the function
# has been removed. The new data loading is tested in test_microsim.py.
