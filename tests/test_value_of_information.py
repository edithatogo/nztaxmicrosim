"""Unit tests for the value_of_information module."""

import numpy as np
import pytest

from src.value_of_information import calculate_evpi


def test_calculate_evpi():
    """EVPI should match manual calculation for a simple example."""
    data = np.array([[100, 150, 130], [120, 140, 125]])
    psa = {"Net Cost": data}
    result = calculate_evpi(psa)
    expected = np.mean(np.max(data, axis=0)) - np.max(np.mean(data, axis=1))
    assert result["Net Cost"] == pytest.approx(expected)


def test_calculate_evpi_invalid_shape():
    """Providing a 1D array should raise a ValueError."""
    psa = {"Metric": np.array([1, 2, 3])}
    with pytest.raises(ValueError):
        calculate_evpi(psa)
