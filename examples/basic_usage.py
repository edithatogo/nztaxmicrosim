from src.microsim import taxit

# Example usage of the taxit function
income = 50000
rates = [0.105, 0.175, 0.30, 0.33, 0.39]
thresholds = [14000, 48000, 70000, 180000]

tax_payable = taxit(income, rates, thresholds)

print(f"For an income of ${income}, the tax payable is: ${tax_payable:.2f}")
