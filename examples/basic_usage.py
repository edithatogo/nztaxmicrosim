from src.microsim import load_parameters, taxit

# Define a sample income
income = 50000

# Load parameters for different tax years from different files
params_2022_23 = load_parameters("src/parameters_2022-2023.json")
params_2024_25 = load_parameters("src/parameters.json")


# Example usage of the taxit function for 2021-2022
params_2021_22 = load_parameters("src/parameters_2021-2022.json")
tax_payable_2021_22 = taxit(
    income,
    params_2021_22["2021-2022"]["tax_brackets"]["rates"],
    params_2021_22["2021-2022"]["tax_brackets"]["thresholds"],
)

print(f"For an income of ${income}, the tax payable in 2021-2022 is: ${tax_payable_2021_22:.2f}")

# Example usage of the taxit function for 2024-2025
tax_payable_2024_25 = taxit(
    income,
    params_2024_25["2024-2025"]["tax_brackets"]["rates"],
    params_2024_25["2024-2025"]["tax_brackets"]["thresholds"],
)

print(f"For an income of ${income}, the tax payable in 2024-2025 is: ${tax_payable_2024_25:.2f}")
