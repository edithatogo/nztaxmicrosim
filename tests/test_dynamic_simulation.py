"""Tests for the dynamic simulation framework."""

import pandas as pd

from src.dynamic_simulation import run_dynamic_simulation
from src.microsim import load_parameters, taxit
from src.parameters import Parameters


def test_year_to_year_progression():
    df = pd.DataFrame({"taxable_income": [30000, 60000]})
    years = ["2022-2023", "2023-2024"]

    results = run_dynamic_simulation(df, years)

    params1 = load_parameters("2022-2023")
    expected1 = [taxit(i, params1.tax_brackets) for i in df["taxable_income"]]
    assert results["2022-2023"]["tax_liability"].tolist() == expected1

    params2 = load_parameters("2023-2024")
    expected2 = [taxit(i, params2.tax_brackets) for i in df["taxable_income"]]
    assert results["2023-2024"]["tax_liability"].tolist() == expected2


def test_labour_response_applied():
    df = pd.DataFrame({"taxable_income": [1000]})
    years = ["2022-2023", "2023-2024"]

    def labour(df: pd.DataFrame, _params: Parameters) -> pd.DataFrame:
        updated = df.copy()
        updated["taxable_income"] *= 1.1
        return updated

    results = run_dynamic_simulation(df, years, labour_response=labour)

    params1 = load_parameters("2022-2023")
    income1 = 1000 * 1.1
    expected1 = taxit(income1, params1.tax_brackets)
    assert results["2022-2023"]["tax_liability"].iloc[0] == expected1

    params2 = load_parameters("2023-2024")
    income2 = 1000 * 1.1 * 1.1
    expected2 = taxit(income2, params2.tax_brackets)
    assert results["2023-2024"]["tax_liability"].iloc[0] == expected2
