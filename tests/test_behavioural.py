import pandas as pd
import pytest
from src.tax_calculator import TaxCalculator
from src.behavioural import labour_supply_response
from src.parameters import Parameters, TaxBracketParams

@pytest.fixture
def sample_population():
    """Provides a sample population DataFrame for testing."""
    data = {
        "person_id": [1, 2, 3],
        "family_id": [1, 1, 2],
        "age": [40, 42, 35],
        "sex": ["Female", "Male", "Female"],
        "income": [50000, 80000, 60000],
    }
    return pd.DataFrame(data)

@pytest.fixture
def tax_calculators():
    """Provides two TaxCalculator instances for a reform scenario."""
    # Baseline parameters (e.g., higher tax rate)
    calc_before = TaxCalculator.from_year("2023-2024")

    # Reform parameters (e.g., lower tax rate)
    calc_after = TaxCalculator.from_year("2023-2024")

    # Make a simple change to the tax brackets for the 'after' scenario
    # We need to create a new Parameters object for the 'after' scenario
    # to avoid modifying the cached parameters.
    params_after = calc_after.params.copy(deep=True)
    params_after.tax_brackets = TaxBracketParams(
        rates=[0.10, 0.15, 0.25, 0.30],
        thresholds=[14000, 48000, 70000]
    )
    calc_after.params = params_after

    return calc_before, calc_after

def test_labour_supply_response(sample_population, tax_calculators):
    """Test the labour_supply_response function."""
    calc_before, calc_after = tax_calculators

    elasticity_params = {
        "primary_earner_intensive_margin": 0.1,
        "secondary_earner_intensive_margin": 0.3,
    }

    # In this scenario, the tax rates go down, so EMTRs should decrease,
    # leading to an increase in labour supply (income).

    # We need to run the simulation once to get the 'after' state without behavioural response
    # For this test, we can assume df_before and df_after are the same initially.
    df_before = sample_population
    df_after_no_behaviour = sample_population.copy()


    df_behavioural = labour_supply_response(
        df_before,
        df_after_no_behaviour,
        calc_before,
        calc_after,
        elasticity_params
    )

    # Check that income has increased for all individuals
    assert (df_behavioural["income"] > df_after_no_behaviour["income"]).all()

    # Check that the secondary earner (person 1) had a larger percentage increase
    # than the primary earner (person 2) in the same family.
    pct_change_person1 = (df_behavioural.loc[0, "income"] - df_after_no_behaviour.loc[0, "income"]) / df_after_no_behaviour.loc[0, "income"]
    pct_change_person2 = (df_behavioural.loc[1, "income"] - df_after_no_behaviour.loc[1, "income"]) / df_after_no_behaviour.loc[1, "income"]

    assert pct_change_person1 > pct_change_person2
