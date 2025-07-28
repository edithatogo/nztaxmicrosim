import argparse
import os
import sys
import time

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "syspop")))
from src.microsim import load_parameters
from src.validation import validate_input_data
from src.wff_microsim import famsim
from syspop.python.input import new_zealand
from syspop.start import create as syspop_create

# --- 0. Argument Parsing ---
parser = argparse.ArgumentParser(description="Run the microsimulation with a synthetic population.")
parser.add_argument(
    "--param_files",
    nargs="+",
    type=str,
    default=["src/parameters.json"],
    help="Paths to the JSON files containing the tax parameters for different years.",
)
parser.add_argument(
    "--population_scale",
    type=float,
    default=1.0,
    help="Scaling factor for the synthetic population (e.g., 0.1 for 10% of original size).",
)
args = parser.parse_args()

# --- 1. Generate Synthetic Population ---
# Define the output directory for the synthetic population
population_dir = "examples/synthetic_population"
os.makedirs(population_dir, exist_ok=True)

# Get the new zealand data
data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "syspop", "etc", "data", "test_data"))
nz_data = new_zealand(data_dir=data_dir, apply_pseudo_ethnicity=False)

# Scale down the population structure if a scaling factor is provided
if args.population_scale != 1.0:
    nz_data["geography"]["population_structure"]["value"] = (
        nz_data["geography"]["population_structure"]["value"] * args.population_scale
    ).astype(int)

print(nz_data["geography"].keys())

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

# Add a small delay to ensure files are written to disk
time.sleep(1)

# Verify files are written
print(f"Listing contents of {population_dir}:")
for item in os.listdir(population_dir):
    print(f"- {item}")

# --- 2. Load the Synthetic Population ---
# The synthetic population is stored in a number of parquet files.
# We will load the ones we need for the microsimulation.
df_people = pd.read_parquet(os.path.abspath(os.path.join(population_dir, "syspop_base.parquet")))
df_households = pd.read_parquet(os.path.abspath(os.path.join(population_dir, "household_data.parquet")))

# Rename columns to match expected names for microsimulation
df_people = df_people.rename(columns={"id": "person_id"})
df_households = df_households.rename(columns={"household": "household_id"})

print(f"Columns in df_people: {df_people.columns.tolist()}")
print(f"Columns in df_households: {df_households.columns.tolist()}")

# --- 3. Transform the Data ---
# The synthetic population data needs to be transformed to match the input
# requirements of the famsim function.
# This will involve renaming columns and creating new ones with default values.

# Merge the people and household dataframes
df = pd.merge(df_people, df_households, on="household_id")

# Rename columns
df = df.rename(columns={"income": "familyinc", "children": "num_children", "id_x": "person_id", "id_y": "household_id"})

# Create required columns with default values
df["maxkiddays"] = 365
df["maxkiddaysbstc"] = 365
df["FTCwgt"] = 1
df["IWTCwgt"] = 1
df["iwtc_elig"] = 1
df["BSTC0wgt"] = 0
df["BSTC01wgt"] = 0
df["BSTC1wgt"] = 0
df["pplcnt"] = df["num_children"] + df["adults"]
df["MFTC_total"] = 0
df["MFTC_elig"] = 0
df["sharedcare"] = 0
df["sharecareFTCwgt"] = 0
df["sharecareBSTC0wgt"] = 0
df["sharecareBSTC01wgt"] = 0
df["MFTCwgt"] = 0
df["iwtc"] = 0
df["selfempind"] = 0

# --- 4. Validate the Transformed Data ---
try:
    df = validate_input_data(df)
    print("Input data validated successfully.")
except ValueError as e:
    print(f"Error: {e}")
    sys.exit(1)

# --- 5. Run the Microsimulation for each parameter file ---
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
