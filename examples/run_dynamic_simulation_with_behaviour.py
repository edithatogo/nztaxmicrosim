import pandas as pd
<<<<<<< HEAD

from src.dynamic_simulation import run_dynamic_simulation
from src.parameters import Parameters, TaxBracketParams

=======
from src.dynamic_simulation import run_dynamic_simulation
from src.parameters import Parameters, TaxBracketParams
from src.tax_calculator import TaxCalculator
>>>>>>> origin/update-a-bunch-of-stuff-5

def main():
    """
    An example script to demonstrate a dynamic simulation with behavioural response.
    """
    print("--- Dynamic Simulation with Behavioural Response Example ---")

    # 1. Define the simulation years and parameters
    years = ["2023-2024", "2024-2025"]

    # We need to manually create the parameter objects to create a 'reform' scenario
    params_2023 = Parameters.from_file("2023-2024")
    params_2024 = Parameters.from_file("2024-2025")

    # Let's create a hypothetical reform in 2024: a simpler, lower tax system
    # This will create a large change in EMTRs and thus a large behavioural response.
<<<<<<< HEAD
    params_2024.tax_brackets = TaxBracketParams(rates=[0.10, 0.20, 0.30], thresholds=[20000, 60000])
=======
    params_2024.tax_brackets = TaxBracketParams(
        rates=[0.10, 0.20, 0.30],
        thresholds=[20000, 60000]
    )
>>>>>>> origin/update-a-bunch-of-stuff-5

    # In a real simulation, you would save these reform parameters to a new JSON
    # and modify `load_parameters` to load them. For this example, we will
    # patch the `load_parameters` function to return our modified params.

<<<<<<< HEAD
    original_load_parameters = pd.read_json  # A bit of a hack to save the original function
=======
    original_load_parameters = pd.read_json # A bit of a hack to save the original function
>>>>>>> origin/update-a-bunch-of-stuff-5

    def mock_load_parameters(year):
        if year == "2023-2024":
            return params_2023
        elif year == "2024-2025":
            return params_2024
        else:
            # For the year before the simulation starts
            return Parameters.from_file(year)

    # 2. Create a sample population
    data = {
        "person_id": [1, 2, 3, 4],
        "family_id": [1, 1, 2, 2],
        "age": [40, 42, 35, 38],
        "sex": ["Female", "Male", "Female", "Male"],
        "income": [60000, 100000, 70000, 90000],
    }
    population_start = pd.DataFrame(data)
    print("\nInitial Population:")
    print(population_start)

    # 3. Define elasticity parameters
    elasticity_params = {
        "primary_earner_intensive_margin": 0.1,
        "secondary_earner_intensive_margin": 0.3,
    }

    # 4. Run the dynamic simulation with behavioural response enabled
    print("\n--- Running Simulation with Behavioural Response ---")

    # We need to patch `microsim.load_parameters` and `dynamic_simulation.load_parameters`
<<<<<<< HEAD
    from src import dynamic_simulation, microsim

=======
    from src import microsim, dynamic_simulation
>>>>>>> origin/update-a-bunch-of-stuff-5
    microsim.load_parameters = mock_load_parameters
    dynamic_simulation.load_parameters = mock_load_parameters

    results = run_dynamic_simulation(
<<<<<<< HEAD
        df=population_start, years=years, use_behavioural_response=True, elasticity_params=elasticity_params
=======
        df=population_start,
        years=years,
        use_behavioural_response=True,
        elasticity_params=elasticity_params
>>>>>>> origin/update-a-bunch-of-stuff-5
    )

    print("\nResults:")
    for year, df_result in results.items():
        print(f"\n--- Year: {year} ---")
        print(df_result)

    # Restore the original function if you were to continue the script
    microsim.load_parameters = original_load_parameters


if __name__ == "__main__":
    main()
