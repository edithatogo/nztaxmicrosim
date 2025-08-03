"""Unit tests for the value_of_information module."""

import numpy as np
import pytest

from src.value_of_information import calculate_evpi, calculate_evppi


def test_calculate_evppi_single_continuous_param():
    """EVPPI should be correctly calculated for a single continuous parameter."""
    # Two options, 1000 simulations
    np.random.seed(42)
    data = np.random.rand(2, 1000) * 100
    # Parameter correlated with the first option being better
    param1 = np.random.rand(1000)
    data[0, :] += param1 * 50

    psa_results = {"Outcome": data}
    psa_parameters = {"param1": param1}

    # EVPPI should be > 0 because param1 is informative
    evppi = calculate_evppi(psa_results, psa_parameters, ["param1"])
    assert "Outcome" in evppi
    assert evppi["Outcome"] > 0

    # EVPPI should be less than or equal to EVPI
    evpi = calculate_evpi(psa_results)
    assert evppi["Outcome"] <= evpi["Outcome"]


def test_calculate_evppi_single_discrete_param():
    """EVPPI should be correctly calculated for a single discrete parameter."""
    data = np.array([[10, 20, 10, 20, 10, 20], [15, 15, 15, 15, 15, 15]])
    # When param is 0, option 1 is better (mean 15 vs 10).
    # When param is 1, option 0 is better (mean 20 vs 15).
    param1 = np.array([0, 1, 0, 1, 0, 1])

    psa_results = {"Cost": data}
    psa_parameters = {"param1": param1}

    evppi = calculate_evppi(psa_results, psa_parameters, ["param1"])

    # Manual calculation:
    # E[Cost | current info] = max(mean(data[0]), mean(data[1])) = max(15, 15) = 15
    # E[Cost | param1=0] = max(mean(10,10,10), mean(15,15,15)) = max(10, 15) = 15
    # E[Cost | param1=1] = max(mean(20,20,20), mean(15,15,15)) = max(20, 15) = 20
    # E[E[Cost | param1]] = 0.5 * 15 + 0.5 * 20 = 7.5 + 10 = 17.5
    # EVPPI = 17.5 - 15 = 2.5
    assert evppi["Cost"] == pytest.approx(2.5)


def test_calculate_evppi_multiple_params():
    """EVPPI should be correctly calculated for multiple parameters."""
    np.random.seed(42)
    data = np.random.rand(2, 100)
    param1 = np.random.rand(100)
    param2 = np.array([0, 1] * 50)

    psa_results = {"Utility": data}
    psa_parameters = {"param1": param1, "param2": param2}

    evppi = calculate_evppi(psa_results, psa_parameters, ["param1", "param2"])
    assert "Utility" in evppi
    assert evppi["Utility"] >= 0


def test_calculate_evppi_no_param_names():
    """EVPPI with an empty param_names list should return 0."""
    np.random.seed(42)
    data = np.random.rand(2, 100)
    param1 = np.random.rand(100)

    psa_results = {"Outcome": data}
    psa_parameters = {"param1": param1}

    evppi = calculate_evppi(psa_results, psa_parameters, [])
    assert evppi["Outcome"] == 0.0


def test_calculate_evppi_invalid_param_name():
    """EVPPI should raise ValueError for an invalid parameter name."""
    np.random.seed(42)
    data = np.random.rand(2, 100)
    psa_results = {"Outcome": data}
    psa_parameters = {"param1": np.random.rand(100)}

    with pytest.raises(ValueError, match="Parameter 'non_existent_param' not found"):
        calculate_evppi(psa_results, psa_parameters, ["non_existent_param"])


def test_calculate_evppi_mismatched_shapes():
    """EVPPI should raise ValueError for mismatched data shapes."""
    np.random.seed(42)
    data = np.random.rand(2, 100)
    param1 = np.random.rand(99)  # Mismatched length

    psa_results = {"Outcome": data}
    psa_parameters = {"param1": param1}

    with pytest.raises(ValueError):
        calculate_evppi(psa_results, psa_parameters, ["param1"])


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
