from src.microsim import load_parameters, taxit

# Load parameters for different tax years
params_2023_24 = load_parameters("2023-2024")
params_2024_25 = load_parameters("2024-2025")

# Example usage of the taxit function for 2023-2024
income = 50000
tax_payable_2023_24 = taxit(
    income,
    params_2023_24["tax_brackets"]["rates"],
    params_2023_24["tax_brackets"]["thresholds"],
)

print(f"For an income of ${income}, the tax payable in 2023-2024 is: ${tax_payable_2023_24:.2f}")

# Example usage of the taxit function for 2024-2025
tax_payable_2024_25 = taxit(
    income,
    params_2024_25["tax_brackets"]["rates"],
    params_2024_25["tax_brackets"]["thresholds"],
)

print(f"For an income of ${income}, the tax payable in 2024-2025 is: ${tax_payable_2024_25:.2f}")
