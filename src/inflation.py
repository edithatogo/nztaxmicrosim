"""
This module provides functionality for adjusting monetary values for inflation.
"""

<<<<<<< HEAD
import json
import os
from pathlib import Path

import pandas as pd
import wbdata
=======
import pandas as pd
import wbdata
import json
from pathlib import Path
import os
>>>>>>> origin/update-a-bunch-of-stuff-5

# Define a cache file for the CPI data
CACHE_DIR = Path(__file__).parent / ".cache"
CPI_CACHE_FILE = CACHE_DIR / "cpi_data.json"

<<<<<<< HEAD

=======
>>>>>>> origin/update-a-bunch-of-stuff-5
def get_cpi_data() -> dict[int, float]:
    """
    Fetches Consumer Price Index (CPI) data from the World Bank, caching it locally.

    The data is for the series 'FP.CPI.TOTL' for New Zealand.

    Returns:
        A dictionary mapping year to CPI value.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)

    if CPI_CACHE_FILE.exists():
        with open(CPI_CACHE_FILE, "r") as f:
            cpi_data = json.load(f)
            # JSON keys are strings, convert them back to integers
            return {int(k): v for k, v in cpi_data.items()}

    print("Fetching CPI data from World Bank API...")
    try:
        # Fetch CPI data for New Zealand. The indicator for CPI is 'FP.CPI.TOTL'.
<<<<<<< HEAD
        cpi_df = wbdata.get_dataframe({"FP.CPI.TOTL": "cpi"}, country="NZL", data_date=None)
=======
        cpi_df = wbdata.get_dataframe(
            {"FP.CPI.TOTL": "cpi"}, country="NZL", data_date=None
        )
>>>>>>> origin/update-a-bunch-of-stuff-5
        # The DataFrame has a multi-index. We want to map year to CPI.
        cpi_df.reset_index(inplace=True)
        cpi_df["date"] = pd.to_numeric(cpi_df["date"])

        # Filter for years where CPI is not null
        cpi_df = cpi_df[cpi_df["cpi"].notna()]

        cpi_data = pd.Series(cpi_df.cpi.values, index=cpi_df.date).to_dict()

        with open(CPI_CACHE_FILE, "w") as f:
            json.dump(cpi_data, f)

        return cpi_data
    except Exception as e:
        print(f"Error fetching data from World Bank API: {e}")
        return {}

<<<<<<< HEAD

=======
>>>>>>> origin/update-a-bunch-of-stuff-5
def adjust_for_inflation(
    data: pd.DataFrame,
    base_year: int,
    target_year: int,
    columns_to_adjust: list[str],
) -> pd.DataFrame:
    """
    Adjusts specified monetary columns of a DataFrame from a target year's
    value to a base year's value.

    For example, to convert 1990 dollars to 2023 dollars, base_year=2023
    and target_year=1990.

    Args:
        data: The pandas DataFrame to adjust.
        base_year: The year to adjust the currency to (e.g., 2023).
        target_year: The year the currency is currently in (e.g., 1990).
        columns_to_adjust: A list of column names in the DataFrame to adjust.

    Returns:
        The DataFrame with the specified columns adjusted for inflation.
    """
    cpi_data = get_cpi_data()

    if not cpi_data:
        print("CPI data is not available. Cannot perform inflation adjustment.")
        return data

    if base_year not in cpi_data:
        raise ValueError(f"CPI data not available for base year: {base_year}")
    if target_year not in cpi_data:
        raise ValueError(f"CPI data not available for target year: {target_year}")

    cpi_base = cpi_data[base_year]
    cpi_target = cpi_data[target_year]

    if cpi_target == 0:
        raise ValueError(f"CPI for target year {target_year} is zero, cannot adjust.")

    adjustment_factor = cpi_base / cpi_target

    print(f"Adjusting from {target_year} to {base_year} with factor: {adjustment_factor:.4f}")

    adjusted_data = data.copy()
    for col in columns_to_adjust:
        if col in adjusted_data.columns:
            adjusted_data[col] = adjusted_data[col] * adjustment_factor
        else:
            print(f"Warning: Column '{col}' not found in DataFrame. Skipping.")

    return adjusted_data
