import os
import sys

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.microsim import calcietc, taxit
from src.wff_microsim import famsim

# --- 1. Create an Artificial Population ---
# This is a small, artificial dataset that has the same structure as the
# output of the syspop tool.
data = {
    "household_id": [1, 1, 2, 2, 2, 3, 4, 4, 5],
    "person_id": [1, 2, 3, 4, 5, 6, 7, 8, 9],
    "age": [35, 34, 45, 42, 12, 28, 55, 53, 18],
    "income": [60000, 75000, 120000, 0, 0, 45000, 80000, 90000, 20000],
    "adults": [2, 2, 2, 2, 2, 1, 2, 2, 1],
    "children": [0, 0, 1, 1, 1, 0, 0, 0, 0],
}
df = pd.DataFrame(data)

# --- 2. Transform the Data ---
# The artificial population data needs to be transformed to match the input
# requirements of the famsim function.
df["familyinc"] = df.groupby("household_id")["income"].transform("sum")
df["num_children"] = df.groupby("household_id")["children"].transform("sum")

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
df["sharecareBSTC1wgt"] = 0
df["MFTCwgt"] = 0
df["iwtc"] = 0
df["selfempind"] = 0

# --- 3. Run the Microsimulation ---

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

# Define placeholder tax parameters for taxit and calcietc (2022 rates)
# These should be updated with 2024-2025 rates as per future roadmap
tax_rates = [0.105, 0.175, 0.30, 0.33, 0.39]
tax_thresholds = [14000, 48000, 70000, 180000]

# IETC parameters (placeholders)
ietc_thrin = 24000
ietc_ent = 520
ietc_thrab = 44000
ietc_abrate = 0.13

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

# Calculate income tax and IETC for each person
df_results["income_tax_payable"] = df_results["income"].apply(lambda x: taxit(x, tax_rates, tax_thresholds))
df_results["ietc_amount"] = df_results.apply(
    lambda row: calcietc(
        row["income"],
        "ys",  # Placeholder, assuming 'ys' for now
        row["FTCcalc"] + row["IWTCcalc"] + row["BSTCcalc"] + row["MFTCcalc"],  # Total WFF as wffamt
        0,  # supamt placeholder
        0,  # benamt placeholder
        ietc_thrin,
        ietc_ent,
        ietc_thrab,
        ietc_abrate,
        0,  # ietc0 placeholder
        row["income"],  # taxinc0 placeholder
    ),
    axis=1,
)
# Calculate net income
df_results["net_income"] = df_results["income"] - df_results["income_tax_payable"] + df_results["ietc_amount"]


# --- 4. Save the Results ---
df_results.to_csv("examples/artificial_population_results.csv", index=False)

print("Successfully generated artificial population and ran microsimulation.")
print("Results saved to examples/artificial_population_results.csv")
