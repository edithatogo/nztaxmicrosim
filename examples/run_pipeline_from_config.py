"""
This script demonstrates how to create and run a simulation pipeline from a YAML configuration file.
"""

import sys
from pathlib import Path

import pandas as pd

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.microsim import load_parameters
from src.pipeline import SimulationPipeline
from src.tax_calculator import TaxCalculator

# --- 1. Load Parameters and Create a Tax Calculator ---
params = load_parameters("2024-2025")
tax_calc = TaxCalculator(params=params)

# --- 2. Create a Sample DataFrame ---
data = {
    "df": pd.DataFrame({
        "familyinc": [50000, 100000, 150000],
        "marital_status": ["Single", "Married", "Single"],
        "num_children": [0, 2, 1],
        "total_individual_income_weekly": [50000 / 52, 100000 / 52, 150000 / 52]
    }),
    "params": params,
    "tax_calc": tax_calc,
}

# --- 3. Create a Pipeline from a Configuration File ---
pipeline = SimulationPipeline.from_config("examples/pipeline_config.yaml")

# --- 4. Run the Pipeline ---
result_data = pipeline.run(data)

# --- 5. Print the Results ---
print("Pipeline Results:")
print(result_data["df"])
