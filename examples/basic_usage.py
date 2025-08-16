import sys
from pathlib import Path

import pandas as pd

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.microsim import load_parameters, taxit
from src.tax_credits import calcietc, family_boost_credit
from src.wff_microsim import famsim

# --- 1. Load Parameters ---
# Load parameters for different tax years
params_2016_17 = load_parameters("2016-2017")
params_2024_25 = load_parameters("2024-2025")

# --- 2. Define a Sample Person/Family ---
income = 60000
family_income = 80000
childcare_costs = 5000
family_details = pd.DataFrame(
    {
        "familyinc": [family_income],
        "FTCwgt": [2],  # 2 children for FTC
        "IWTCwgt": [2],  # 2 children for IWTC
        "BSTC0wgt": [0],
        "BSTC01wgt": [0],
        "BSTC1wgt": [1],  # 1 child for BSTC
        "MFTCwgt": [0],
        "iwtc_elig": [12],
        "pplcnt": [4],
        "MFTC_total": [0],
        "MFTC_elig": [0],
        "sharedcare": [0],
        "sharecareFTCwgt": [0],
        "sharecareBSTC0wgt": [0],
        "sharecareBSTC01wgt": [0],
        "sharecareBSTC1wgt": [0],
        "iwtc": [1],
        "selfempind": [0],
        "maxkiddays": [365],
        "maxkiddaysbstc": [365],
    }
)


# --- 3. Calculate Tax and Credits for 2016-2017 ---
output_lines = []
output_lines.append("--- Calculating for 2016-2017 ---")

# Calculate income tax
tax_16_17 = taxit(
    income,
    params_2016_17.tax_brackets,
)
output_lines.append(f"Income Tax for an income of ${income}: ${tax_16_17:.2f}")

# Calculate IETC
ietc_16_17 = 0.0
if params_2016_17.ietc is not None:
    ietc_16_17 = calcietc(
        taxable_income=income,
        is_wff_recipient=False,
        is_super_recipient=False,
        is_benefit_recipient=False,
        ietc_params=params_2016_17.ietc,
    )
output_lines.append(f"IETC: ${ietc_16_17:.2f}")

# Calculate WFF credits
if params_2016_17.wff is not None:
    wff_16_17 = famsim(
        family_details.copy(),
        wff_params=params_2016_17.wff,
        wagegwt=0,
        daysinperiod=365,
    )
    output_lines.append("Working for Families Entitlements:")
    output_lines.append(wff_16_17[["FTCcalc", "IWTCcalc", "BSTCcalc", "MFTCcalc"]].round(2).to_string())


# --- 4. Calculate Tax and Credits for 2024-2025 ---
output_lines.append("\n--- Calculating for 2024-2025 ---")

# Calculate income tax
tax_24_25 = taxit(
    income,
    params_2024_25.tax_brackets,
)
output_lines.append(f"Income Tax for an income of ${income}: ${tax_24_25:.2f}")

# Calculate IETC
ietc_24_25 = 0.0
if params_2024_25.ietc is not None:
    ietc_24_25 = calcietc(
        taxable_income=income,
        is_wff_recipient=False,
        is_super_recipient=False,
        is_benefit_recipient=False,
        ietc_params=params_2024_25.ietc,
    )
output_lines.append(f"IETC: ${ietc_24_25:.2f}")

# Calculate WFF credits
if params_2024_25.wff is not None:
    wff_24_25 = famsim(
        family_details.copy(),
        wff_params=params_2024_25.wff,
        wagegwt=0,
        daysinperiod=365,
    )
    output_lines.append("Working for Families Entitlements:")
    output_lines.append(wff_24_25[["FTCcalc", "IWTCcalc", "BSTCcalc", "MFTCcalc"]].round(2).to_string())

# Calculate FamilyBoost credit
# Note: FamilyBoost is not available in 2016-2017, so we only calculate it for 2024-2025
if (
    hasattr(params_2024_25, "family_boost")
    and params_2024_25.family_boost is not None
    and params_2024_25.family_boost.max_credit > 0
):
    family_boost = family_boost_credit(
        family_income=family_income,
        childcare_costs=childcare_costs,
        family_boost_params=params_2024_25.family_boost,
    )
    if family_boost > 0:
        output_lines.append(f"FamilyBoost Credit: ${family_boost:.2f}")

with open("basic_usage_output.txt", "w") as f:
    for line in output_lines:
        f.write(line + "\n")
