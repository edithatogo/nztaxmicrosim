"""Tests for the historical_data module."""

from src.historical_data import get_historical_parameters, load_historical_data


def test_load_historical_data():
    """Tests that the historical data can be loaded."""
    data = load_historical_data()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "year" in data[0]
    assert "description" in data[0]
    assert "rates" in data[0]


def test_get_historical_parameters_tax_brackets():
    """Tests that historical parameters can be retrieved and transformed."""
    # Test a year that should be in the historical data
    params = get_historical_parameters("2021-2022")

    assert params.tax_brackets is not None
    assert params.tax_brackets.rates == [0.105, 0.175, 0.30, 0.33, 0.39]
    assert params.tax_brackets.thresholds == [14000, 48000, 70000, 180000]
