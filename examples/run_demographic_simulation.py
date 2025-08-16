import pandas as pd
from src.demographic_modelling import age_population_forward


def main():
    """
    An example script to demonstrate the use of the demographic modelling module.
    """
    print("--- Demographic Modelling Example ---")

    # 1. Create a sample population DataFrame for the year 1990.
    # In a real scenario, this data would be loaded from a file.
    data = {
        "person_id": [1, 2, 3, 4, 5],
        "family_id": [1, 1, 2, 2, 3],
        "age": [30, 32, 25, 28, 45],
        "sex": ["Female", "Male", "Female", "Male", "Female"],
        "income": [50000, 70000, 40000, 60000, 90000],
    }
    population_1990 = pd.DataFrame(data)

    print("\nOriginal population (1990):")
    print(population_1990)
    print(f"Total population: {len(population_1990)}")

    # 2. Call the function to age the population forward by one year.
    # This will simulate births based on the fertility data for 1990
    # found in `src/data/fertility_rates.json`.
    try:
        population_1991 = age_population_forward(
            df=population_1990,
            year=1990
        )

        print("\nNew population (1991):")
        print(population_1991)
        print(f"Total population: {len(population_1991)}")

        # You could now run this new population through another year
        # population_1992 = age_population_forward(
        #     df=population_1991,
        #     year=1991
        # )
        # print("\nNew population (1992):")
        # print(population_1992)

    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
