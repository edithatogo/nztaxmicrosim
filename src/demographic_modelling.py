"""
This module provides functionality for demographic modelling, such as aging a
population and simulating births.
"""

import pandas as pd
import json
from pathlib import Path
import random
import numpy as np

# Define the path to the fertility data
DATA_DIR = Path(__file__).parent / "data"
FERTILITY_DATA_FILE = DATA_DIR / "fertility_rates.json"


def get_fertility_data() -> dict:
    """
    Loads age-specific fertility rate data from a local JSON file.

    Note: The data in `src/data/fertility_rates.json` is a placeholder.
    A developer should replace this with real, comprehensive data from
    a source like Stats NZ Infoshare.

    Returns:
        A dictionary where keys are years (as strings) and values are
        dictionaries mapping age groups to fertility rates (births per 1000 women).
    """
    if not FERTILITY_DATA_FILE.exists():
        print(f"Warning: Fertility data file not found at {FERTILITY_DATA_FILE}")
        return {}

    with open(FERTILITY_DATA_FILE, "r") as f:
        return json.load(f)


def _get_rate_for_age(age: int, rates_for_year: dict) -> float:
    """Helper function to find the fertility rate for a specific age."""
    for age_range, rate in rates_for_year.items():
        if age_range == "comment":
            continue
        low, high = map(int, age_range.split('-'))
        if low <= age <= high:
            return rate / 1000.0 # Convert from per 1000 women to a probability
    return 0.0

def age_population_forward(df: pd.DataFrame, year: int) -> pd.DataFrame:
    """
    Ages a population DataFrame forward by one year and simulates births.

    This function performs two main operations:
    1.  Increments the 'age' of every individual in the DataFrame by 1.
    2.  Simulates new births based on age-specific fertility rates for the
        given year. It assumes the presence of 'age', 'sex', and 'family_id'
        columns. 'sex' is expected to be 'Male' or 'Female'.

    Args:
        df: The input population as a pandas DataFrame.
        year: The starting year of the population. The function will simulate
              events to create the population for year + 1.

    Returns:
        A new pandas DataFrame representing the population in the next year.
    """
    print(f"Aging population from {year} to {year + 1}...")

    # 1. Age the existing population
    aged_df = df.copy()
    aged_df["age"] = aged_df["age"] + 1

    # 2. Simulate births
    fertility_data = get_fertility_data()
    year_str = str(year)

    if year_str not in fertility_data:
        print(f"Warning: No fertility data for year {year}. No births will be simulated.")
        return aged_df

    rates_for_year = fertility_data[year_str]

    women_of_childbearing_age = aged_df[
        (aged_df["sex"] == "Female") & (aged_df["age"] >= 15) & (aged_df["age"] <= 49)
    ]

    new_births = []

    for _, woman in women_of_childbearing_age.iterrows():
        fertility_rate = _get_rate_for_age(woman["age"], rates_for_year)
        if random.random() < fertility_rate:
            # A birth occurs!
            new_baby = {
                # Inherit family-level characteristics
                "family_id": woman["family_id"],
                "region": woman.get("region", "Unknown"),
                # Baby-specific characteristics
                "age": 0,
                "sex": random.choice(["Male", "Female"]),
                # Assume babies have no income or assets initially
                "income": 0,
                "assets": 0,
            }
            # Add other columns with default values if they exist in the dataframe
            for col in aged_df.columns:
                if col not in new_baby:
                    new_baby[col] = 0

            new_births.append(new_baby)

    if new_births:
        print(f"Simulated {len(new_births)} new births.")
        babies_df = pd.DataFrame(new_births)
        final_df = pd.concat([aged_df, babies_df], ignore_index=True)
    else:
        print("No births were simulated.")
        final_df = aged_df

    return final_df
