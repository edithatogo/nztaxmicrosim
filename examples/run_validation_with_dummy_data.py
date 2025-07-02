import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.microsim import load_parameters
from src.wff_microsim import famsim
from src.validation import validate_input_data

# --- 1. Create a dummy DataFrame ---
data = {
    'person_id': [1, 2, 3, 4, 5],
    'household_id': [1, 1, 2, 2, 3],
    'familyinc': [50000, 0, 75000, 25000, 100000],
    'num_children': [2, 2, 1, 1, 0],
    'adults': [2, 2, 2, 2, 1],
    'maxkiddays': [365, 365, 365, 365, 365],
    'maxkiddaysbstc': [365, 365, 365, 365, 365],
    'FTCwgt': [1, 1, 1, 1, 1],
    'IWTCwgt': [1, 1, 1, 1, 1],
    'iwtc_elig': [1, 1, 1, 1, 1],
    'BSTC0wgt': [0, 0, 0, 0, 0],
    'BSTC01wgt': [0, 0, 0, 0, 0],
    'BSTC1wgt': [0, 0, 0, 0, 0],
    'pplcnt': [4, 4, 3, 3, 1],
    'MFTC_total': [0, 0, 0, 0, 0],
    'MFTC_elig': [0, 0, 0, 0, 0],
    'sharedcare': [0, 0, 0, 0, 0],
    'sharecareFTCwgt': [0, 0, 0, 0, 0],
    'sharecareBSTC0wgt': [0, 0, 0, 0, 0],
    'sharecareBSTC01wgt': [0, 0, 0, 0, 0],
    'sharecareBSTC1wgt': [0, 0, 0, 0, 0],
    'MFTCwgt': [0, 0, 0, 0, 0],
    'iwtc': [0, 0, 0, 0, 0],
    'selfempind': [0, 0, 0, 0, 0]
}
df = pd.DataFrame(data)

# --- 2. Validate the dummy data ---
try:
    df = validate_input_data(df)
    print("Dummy data validated successfully.")
except ValueError as e:
    print(f"Error: {e}")
    sys.exit(1)

# --- 3. Run the Microsimulation ---
# Use the 2024-2025 parameters by default
params = load_parameters("2024-2025")
wff_params = params["wff"]
wagegwt = 0.03
daysinperiod = 365

df_results = famsim(
    df.copy(),
    wff_params,
    wagegwt,
    daysinperiod,
)

# --- 4. Save the Results ---
results_filename = "dummy_data_results.csv"
results_path = os.path.join("examples", results_filename)
df_results.to_csv(results_path, index=False)
print(f"Successfully ran microsimulation with dummy data.")
print(f"Results saved to {results_path}")
