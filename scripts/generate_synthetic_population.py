import os

import numpy as np
import pandas as pd
from faker import Faker

# Initialize Faker
fake = Faker("en_NZ")

# Define the number of people to generate
NUM_PEOPLE = 500


def generate_synthetic_population():
    """Generates a synthetic population dataset and saves it to a CSV file."""

    data = []
    for i in range(1, NUM_PEOPLE + 1):
        age = fake.random_int(min=18, max=75)
        employment_status = np.random.choice(["Employed", "Unemployed", "Not in Labour Force"], p=[0.6, 0.1, 0.3])

        if employment_status == "Employed":
            employment_income = np.random.lognormal(mean=np.log(60000), sigma=0.5)
            self_employment_income = np.random.choice(
                [0, np.random.lognormal(mean=np.log(10000), sigma=0.8)], p=[0.8, 0.2]
            )
            hours_worked = np.random.choice([20, 30, 40, 50])
        else:
            employment_income = 0
            self_employment_income = 0
            hours_worked = 0

        is_jss_recipient = (employment_status == "Unemployed") and (age < 65)

        num_children = np.random.choice([0, 1, 2, 3, 4], p=[0.5, 0.2, 0.2, 0.05, 0.05])

        person = {
            "person_id": i,
            "household_id": i,  # Simplifying to one person per household for now
            "age": age,
            "gender": np.random.choice(["Male", "Female"]),
            "marital_status": np.random.choice(["Single", "Married", "Divorced"]),
            "family_household_type": "Single adult" if num_children == 0 else "Sole parent",
            "household_size": 1 + num_children,
            "num_children": num_children,
            "adults": 1,
            "ages_of_children": [fake.random_int(min=0, max=18) for _ in range(num_children)],
            "region": fake.city(),
            "disability_status": np.random.choice([True, False], p=[0.1, 0.9]),
            "employment_income": employment_income,
            "self_employment_income": self_employment_income,
            "investment_income": np.random.lognormal(mean=np.log(500), sigma=1.0) if np.random.rand() > 0.5 else 0,
            "rental_property_income": 0,
            "private_pensions_annuities": 0,
            "employment_status": employment_status,
            "hours_worked": hours_worked,
            "is_jss_recipient": is_jss_recipient,
            "is_sps_recipient": (num_children > 0) and (employment_status != "Employed"),
            "is_slp_recipient": False,
            "is_nz_super_recipient": age >= 65,
            "housing_costs": np.random.randint(150, 600),
            "familyinc": 0,  # To be calculated
            "FTCwgt": 1,
            "IWTCwgt": 1,
            "BSTC0wgt": 1,
            "BSTC01wgt": 1,
            "BSTC1wgt": 1,
            "MFTCwgt": 1,
            "iwtc_elig": 1,
            "MFTC_total": 1000,
            "MFTC_elig": 1,
            "sharedcare": 0,
            "sharecareFTCwgt": 0,
            "sharecareBSTC0wgt": 0,
            "sharecareBSTC01wgt": 0,
            "sharecareBSTC1wgt": 0,
            "iwtc": 1,
            "selfempind": 1 if self_employment_income > 0 else 0,
            "maxkiddays": 365,
            "maxkiddaysbstc": 365,
            "pplcnt": 1 + num_children,
        }
        data.append(person)

    df = pd.DataFrame(data)

    # Calculate familyinc
    df["familyinc"] = df["employment_income"] + df["self_employment_income"] + df["investment_income"]

    # Define the output path
    output_dir = "src/data"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "default_population.csv")

    # Save to CSV
    df.to_csv(output_path, index=False)

    print(f"Successfully generated synthetic population at {output_path}")


if __name__ == "__main__":
    generate_synthetic_population()
