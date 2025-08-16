import pandas as pd
from src.inflation import adjust_for_inflation


def main():
    """
    An example script to demonstrate the use of the inflation adjustment module.
    """
    print("--- Inflation Adjustment Example ---")

    # 1. Create a sample DataFrame.
    # In a real scenario, this data would be loaded from a file.
    data = {
        "person_id": [1, 2, 3],
        "income_1990": [25000, 60000, 120000],
        "assets_1990": [50000, 250000, 800000],
        "region": ["Auckland", "Wellington", "Auckland"],
    }
    df_1990 = pd.DataFrame(data)

    print("\nOriginal DataFrame (in 1990 NZD):")
    print(df_1990)

    # 2. Define the adjustment parameters.
    # We want to see what these 1990 values would be in 2022 dollars.
    base_year = 2022
    target_year = 1990
    columns_to_adjust = ["income_1990", "assets_1990"]

    # 3. Call the adjustment function.
    # The first time this runs, it may take a moment to download the CPI data.
    # Subsequent runs will be faster due to caching.
    try:
        df_2022 = adjust_for_inflation(
            data=df_1990,
            base_year=base_year,
            target_year=target_year,
            columns_to_adjust=columns_to_adjust,
        )

        print(f"\nAdjusted DataFrame (in {base_year} NZD):")
        print(df_2022)

    except ValueError as e:
        print(f"\nAn error occurred during adjustment: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
