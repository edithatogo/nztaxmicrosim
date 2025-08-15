<<<<<<< HEAD
import os

import numpy as np
import pandas as pd
import yaml

from src.reporting_framework import (
    HistoricalBenefitEntitlementsChart,
    HistoricalEffectiveTaxRateChart,
    HistoricalGiniChart,
    HistoricalPovertyRateChart,
    ReportGenerator,
)


def generate_dummy_data_for_year(year: int) -> pd.DataFrame:
    """Generates a sample DataFrame for a given year with some noise."""
    np.random.seed(year)  # Use year as seed for reproducibility
=======
import yaml
import pandas as pd
import numpy as np
import os
from src.reporting_framework import (
    ReportGenerator,
    HistoricalGiniChart,
    HistoricalPovertyRateChart,
    HistoricalEffectiveTaxRateChart,
    HistoricalBenefitEntitlementsChart,
)

def generate_dummy_data_for_year(year: int) -> pd.DataFrame:
    """Generates a sample DataFrame for a given year with some noise."""
    np.random.seed(year) # Use year as seed for reproducibility
>>>>>>> origin/update-a-bunch-of-stuff-5
    num_people = 500

    # Base values that increase over time
    base_income = 30000 + (year - 1990) * 1000
    base_tax = 4000 + (year - 1990) * 200
    base_benefits = 500 + (year - 1990) * 50

    data = {
        "familyinc": np.random.normal(base_income, 15000, num_people).clip(min=0),
        "tax_liability": np.random.normal(base_tax, 2000, num_people).clip(min=0),
        "jss_entitlement": np.random.normal(base_benefits, 100, num_people).clip(min=0),
    }
    df = pd.DataFrame(data)
    # This is a simplified disposable income calculation for demonstration
    df["disposable_income"] = df["familyinc"] - df["tax_liability"] + df["jss_entitlement"]
    return df

<<<<<<< HEAD

=======
>>>>>>> origin/update-a-bunch-of-stuff-5
def main():
    """
    An example script to generate a historical report from a YAML configuration.
    """
    print("--- Historical Report Generation Example ---")

    # 1. Load the configuration file
    config_path = "examples/historical_report_config.yml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    print(f"Loaded configuration from {config_path}")

    # 2. Load or generate data for the specified years
    print("Generating dummy data for specified years...")
<<<<<<< HEAD
    historical_data = {year: generate_dummy_data_for_year(year) for year in config["years_to_include"]}
=======
    historical_data = {
        year: generate_dummy_data_for_year(year) for year in config["years_to_include"]
    }
>>>>>>> origin/update-a-bunch-of-stuff-5
    print(f"Generated data for years: {list(historical_data.keys())}")

    # 3. Map report names from config to component classes
    component_map = {
        "HistoricalGiniChart": HistoricalGiniChart,
        "HistoricalPovertyRateChart": HistoricalPovertyRateChart,
        "HistoricalEffectiveTaxRateChart": HistoricalEffectiveTaxRateChart,
        "HistoricalBenefitEntitlementsChart": HistoricalBenefitEntitlementsChart,
    }

    # 4. Instantiate the requested report components
    components_to_run = []
    for report_name in config["reports_to_generate"]:
        if report_name in component_map:
            components_to_run.append(component_map[report_name]())
        else:
            print(f"Warning: Unknown report component '{report_name}' in config. Skipping.")

    if not components_to_run:
        print("No valid report components specified in the config. Exiting.")
        return

    # 5. Generate the report
    report_gen = ReportGenerator(components_to_run)

    print("Generating report components...")
    for component in components_to_run:
        # The generate method for historical components expects a dictionary of dataframes
        report_gen.generated_content[component.title] = component.generate(
            historical_data, config.get("report_parameters", {})
        )

    # 6. Compile to a Markdown file
    output_path = "historical_report_example.md"
    report_markdown = report_gen.to_markdown_report()

    with open(output_path, "w") as f:
        f.write(report_markdown)

    print(f"\nSuccessfully generated historical report at: {output_path}")
    # Also ensure the reports directory exists for the images
    os.makedirs("reports", exist_ok=True)


if __name__ == "__main__":
    main()
