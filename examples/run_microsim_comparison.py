import argparse
import os
import sys
import time

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from syspop.python.input import new_zealand
from syspop.start import create as syspop_create

from src.microsim import load_parameters
from src.validation import SimulationInputSchema, validate_input_data
from src.wff_microsim import famsim

# --- 0. Argument Parsing ---
parser = argparse.ArgumentParser(description="Run the microsimulation for multiple years with a synthetic population.")
parser.add_argument(
    "--param_files",
    nargs="+",
    type=str,
    required=True,
    help="Paths to the JSON files containing the tax parameters for different years.",
)
parser.add_argument(
    "--population_scale",
    type=float,
    default=0.01,  # Default to a smaller population for faster testing
    help="Scaling factor for the synthetic population (e.g., 0.1 for 10% of original size).",
)
args = parser.parse_args()

# --- 1. Generate Synthetic Population (if not already generated) ---
population_dir = "examples/synthetic_population"
os.makedirs(population_dir, exist_ok=True)
syspop_full_path = os.path.abspath(os.path.join(population_dir, "syspop_full.parquet"))

if not os.path.exists(syspop_full_path):
    print("\n--- Generating synthetic population ---")
    # Get the new zealand data
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "syspop", "etc", "data", "test_data"))
    nz_data = new_zealand(data_dir=data_dir, apply_pseudo_ethnicity=False)

    # Scale down the population structure if a scaling factor is provided
    if args.population_scale != 1.0:
        nz_data["geography"]["population_structure"]["value"] = (
            nz_data["geography"]["population_structure"]["value"] * args.population_scale
        ).astype(int)

    print(f"NZ Data Geography Keys: {nz_data['geography'].keys()}")

    # Get the list of statistical areas
    syn_areas = list(nz_data["geography"]["geography_hierarchy"]["area"])

    # Create the synthetic population
    syspop_create(
        syn_areas,
        population_dir,
        population={"structure": nz_data["geography"]["population_structure"]},
        geography={
            "hierarchy": nz_data["geography"]["geography_hierarchy"],
            "location": nz_data["geography"]["geography_location"],
            "address": nz_data["geography"]["geography_address"],
        },
        household={"composition": nz_data["geography"]["household_composition"]},
        work={
            "employee": nz_data["geography"]["work_employee"],
            "employer": nz_data["geography"]["work_employer"],
            "income": nz_data["geography"]["work_income"],
        },
        commute={
            "travel_to_work": nz_data["geography"]["commute_travel_to_work"],
            "travel_to_school": nz_data["geography"]["commute_travel_to_school"],
        },
        education={"school": nz_data["geography"]["school"], "kindergarten": nz_data["geography"]["kindergarten"]},
        shared_space={
            "hospital": nz_data["geography"]["hospital"],
            "bakery": nz_data["geography"]["shared_space_bakery"],
            "cafe": nz_data["geography"]["shared_space_cafe"],
            "department_store": nz_data["geography"]["shared_space_department_store"],
            "fast_food": nz_data["geography"]["shared_space_fast_food"],
            "park": nz_data["geography"]["shared_space_park"],
            "pub": nz_data["geography"]["shared_space_pub"],
            "restaurant": nz_data["geography"]["shared_space_restaurant"],
            "supermarket": nz_data["geography"]["shared_space_supermarket"],
            "wholesale": nz_data["geography"]["shared_space_wholesale"],
        },
    )
    print(f"Listing contents of {population_dir} after generation:")
    for item in os.listdir(population_dir):
        print(f"- {item}")
    time.sleep(1)  # Small delay to ensure file system sync

# --- 2. Load the Synthetic Population ---
print(f"\n--- Loading synthetic population from {syspop_full_path} ---")
df = pd.read_parquet(syspop_full_path)

print(f"Columns in loaded population DataFrame: {df.columns.tolist()}")
print(f"First 5 rows of loaded population DataFrame:\n{df.head().to_markdown()}")

# --- 3. Transform the Data for Microsimulation ---
# Rename columns to match expected names for microsimulation
df = df.rename(
    columns={"income": "familyinc", "household": "household_id", "id": "person_id", "children": "num_children"}
)

# Convert 'familyinc' to numeric, coercing errors and filling NaN with 0
df["familyinc"] = pd.to_numeric(df["familyinc"], errors="coerce").fillna(0)

# Create required columns with default values
df["maxkiddays"] = 365
df["maxkiddaysbstc"] = 365
df["FTCwgt"] = 1
df["IWTCwgt"] = 1
df["iwtc_elig"] = 1
df["BSTC0wgt"] = 0
df["BSTC01wgt"] = 0
df["BSTC1wgt"] = 0
df["MFTC_total"] = 0
df["MFTC_elig"] = 0
df["sharedcare"] = 0
df["sharecareFTCwgt"] = 0
df["sharecareBSTC0wgt"] = 0
df["sharecareBSTC01wgt"] = 0
df["sharecareBSTC1wgt"] = 0
df["MFTCwgt"] = 0
df["iwtc"] = 0
df["selfempind"] = 0

# Ensure children and adults are numeric if they aren't already
df["num_children"] = df["num_children"].fillna(0).astype(int)
df["adults"] = df["adults"].fillna(0).astype(int)
df["pplcnt"] = df["num_children"] + df["adults"]

# Validate the transformed data
schema_cols = list(SimulationInputSchema.model_fields.keys())
try:
    validated_subset = validate_input_data(df[schema_cols])
    df.update(validated_subset)
except ValueError as e:
    print(f"Error: {e}")
    sys.exit(1)


# --- 4. Run the Microsimulation for each parameter file ---
for param_file in args.param_files:
    year = os.path.basename(param_file).split("_")[1].split(".")[0]
    print(f"\n--- Running microsimulation with parameters from: {param_file} ({year}) ---")
    params = load_parameters(year)
    wff_params = params["wff"]

    # Define the parameters for the famsim function
    wagegwt = 0.03
    daysinperiod = 365

    # Run the famsim function
    df_results = famsim(
        df.copy(),  # Use a copy to avoid modifying the original DataFrame in the loop
        wff_params,
        wagegwt,
        daysinperiod,
    )

    # --- 5. Save the Results ---
    results_filename = f"synthetic_population_results_{year}.csv"
    results_path = os.path.join(population_dir, results_filename)
    df_results.to_csv(results_path, index=False)
    print(f"Successfully ran microsimulation for {year}.")
    print(f"Results saved to {results_path}")

print("\n--- All microsimulations complete ---\n")
