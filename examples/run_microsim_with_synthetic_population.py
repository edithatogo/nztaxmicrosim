import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.wff_microsim import famsim
from syspop.python.input import new_zealand
from syspop.start import create as syspop_create

# --- 1. Generate Synthetic Population ---
# Define the output directory for the synthetic population
population_dir = "examples/synthetic_population"
os.makedirs(population_dir, exist_ok=True)

# Get the new zealand data
nz_data = new_zealand(apply_pseudo_ethnicity=False)
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

# --- 2. Load the Synthetic Population ---
# The synthetic population is stored in a number of parquet files.
# We will load the ones we need for the microsimulation.
df_people = pd.read_parquet(os.path.join(population_dir, "people.parquet"))
df_households = pd.read_parquet(os.path.join(population_dir, "households.parquet"))

# --- 3. Transform the Data ---
# The synthetic population data needs to be transformed to match the input
# requirements of the famsim function.
# This will involve renaming columns and creating new ones with default values.

# Merge the people and household dataframes
df = pd.merge(df_people, df_households, on="household_id")

# Rename columns
df = df.rename(columns={
    "income": "familyinc",
    "children": "num_children",
    "id_x": "person_id",
    "id_y": "household_id"
})

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

# --- 4. Run the Microsimulation ---
# Define the parameters for the famsim function
ftc1 = 5000
ftc2 = 3000
iwtc1 = 1000
iwtc2 = 500
bstc = 3000
mftc = 25000
abatethresh1 = 42700
abatethresh2 = 100000
abaterate1 = 0.27
abaterate2 = 0.3
bstcthresh = 42700
bstcabate = 0.27
wagegwt = 0.03
daysinperiod = 365

# Run the famsim function
df_results = famsim(
    df,
    ftc1,
    ftc2,
    iwtc1,
    iwtc2,
    bstc,
    mftc,
    abatethresh1,
    abatethresh2,
    abaterate1,
    abaterate2,
    bstcthresh,
    bstcabate,
    wagegwt,
    daysinperiod,
)

# --- 5. Save the Results ---
df_results.to_csv("examples/synthetic_population_results.csv", index=False)

print("Successfully generated synthetic population and ran microsimulation.")
print("Results saved to examples/synthetic_population_results.csv")
