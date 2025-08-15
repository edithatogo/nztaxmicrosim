import pandas as pd
import pytest
import os
from src.reporting_framework import (
    HistoricalGiniChart,
    HistoricalPovertyRateChart,
    HistoricalEffectiveTaxRateChart,
    HistoricalBenefitEntitlementsChart,
)
import matplotlib.pyplot as plt


@pytest.fixture
def sample_historical_data():
    """Provides a sample dictionary of DataFrames for historical testing."""
    data_1990 = {
        "familyinc": [20000, 40000, 60000],
        "tax_liability": [2000, 5000, 10000],
        "jss_entitlement": [1000, 0, 0],
    }
    df_1990 = pd.DataFrame(data_1990)
    # Add required disposable_income column
    df_1990["disposable_income"] = df_1990["familyinc"] - df_1990["tax_liability"] + df_1990["jss_entitlement"]

    data_2020 = {
        "familyinc": [40000, 80000, 120000],
        "tax_liability": [4000, 12000, 25000],
        "jss_entitlement": [2000, 0, 0],
    }
    df_2020 = pd.DataFrame(data_2020)
    df_2020["disposable_income"] = df_2020["familyinc"] - df_2020["tax_liability"] + df_2020["jss_entitlement"]

    return {1990: df_1990, 2020: df_2020}


def test_historical_gini_chart(sample_historical_data):
    """Test the HistoricalGiniChart component."""
    component = HistoricalGiniChart()
    fig = component.generate(sample_historical_data, {})

    assert isinstance(fig, plt.Figure)

    # Test markdown generation and file saving
    md = component.to_markdown(fig)
    filepath = "reports/gini_coefficient_over_time.png"
    assert os.path.exists(filepath)
    assert f"![{component.title}]({filepath})" in md
    os.remove(filepath) # Clean up


def test_historical_poverty_rate_chart(sample_historical_data):
    """Test the HistoricalPovertyRateChart component."""
    component = HistoricalPovertyRateChart()
    params = {"poverty_line_relative": 0.5}
    fig = component.generate(sample_historical_data, params)

    assert isinstance(fig, plt.Figure)

    md = component.to_markdown(fig)
    filepath = "reports/poverty_rate_over_time.png"
    assert os.path.exists(filepath)
    assert f"![{component.title}]({filepath})" in md
    os.remove(filepath)


def test_historical_effective_tax_rate_chart(sample_historical_data):
    """Test the HistoricalEffectiveTaxRateChart component."""
    component = HistoricalEffectiveTaxRateChart()
    fig = component.generate(sample_historical_data, {})

    assert isinstance(fig, plt.Figure)

    md = component.to_markdown(fig)
    filepath = "reports/effective_tax_rate_over_time.png"
    assert os.path.exists(filepath)
    assert f"![{component.title}]({filepath})" in md
    os.remove(filepath)


def test_historical_benefit_entitlements_chart(sample_historical_data):
    """Test the HistoricalBenefitEntitlementsChart component."""
    component = HistoricalBenefitEntitlementsChart()
    fig = component.generate(sample_historical_data, {})

    assert isinstance(fig, plt.Figure)

    md = component.to_markdown(fig)
    filepath = "reports/average_benefit_entitlement_over_time.png"
    assert os.path.exists(filepath)
    assert f"![{component.title}]({filepath})" in md
    os.remove(filepath)