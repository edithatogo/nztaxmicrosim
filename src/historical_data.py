"""This module handles loading and transformation of historical tax data."""

import json
import os
import re
from typing import Any, Dict, List

from .parameters import Parameters


def load_historical_data() -> List[Dict[str, Any]]:
    """Loads the historical tax data from the JSON file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "data", "nz_personal_tax_full.json")

    if not os.path.exists(file_path):
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def transform_historical_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforms a single record from the historical data file into a format
    that aligns with the Parameters model.
    """
    transformed_record = {}

    # Transform tax brackets
    if "rates" in record and all("threshold" in r for r in record["rates"]):
        rates = []
        thresholds = []
        for r in record["rates"]:
            # Extract rate
            rate_match = re.search(r"(\d+\.?\d*)%", r.get("rate", ""))
            if rate_match:
                rates.append(float(rate_match.group(1)) / 100.0)
            else:
                continue

            # Extract threshold
            threshold_str = r.get("threshold", "")
            threshold_match = re.findall(r"\d{1,3}(?:,\d{3})*", threshold_str)
            if threshold_match:
                # Get the last number in the threshold string, which is the upper bound
                thresholds.append(int(threshold_match[-1].replace(",", "")))

        # The last threshold is for income "over" a certain amount, so we don't include it
        if len(thresholds) == len(rates):
            thresholds.pop()

        if rates and (len(thresholds) == len(rates) - 1):
            transformed_record["tax_brackets"] = {
                "rates": rates,
                "thresholds": thresholds,
            }

    return transformed_record


def get_historical_parameters(year_str: str) -> Parameters:
    """
    Gets the parameters for a given year from the historical data.
    """
    from .microsim import load_parameters

    historical_data = load_historical_data()

    year = int(year_str.split("-")[0])

    # Find the most recent record for the given year
    relevant_record = None
    for record in historical_data:
        try:
            record_year_str = str(record.get("year", ""))
            record_year = int(re.split(r"[/ ]", record_year_str)[0])
            if record_year <= year:
                if relevant_record is None:
                    relevant_record = record
                else:
                    current_best_year = int(re.split(r"[/ ]", str(relevant_record.get("year", "")))[0])
                    if record_year > current_best_year:
                        relevant_record = record
        except (ValueError, TypeError, IndexError):
            continue

    if relevant_record:
        # Start with the most recent complete parameters, and override with historical data
        # Find the most recent parameter file available
        script_dir = os.path.dirname(os.path.abspath(__file__))
        param_files = [f for f in os.listdir(script_dir) if f.startswith("parameters_") and f.endswith(".json")]
        latest_param_file = sorted(param_files, reverse=True)[0]
        latest_year = latest_param_file.replace("parameters_", "").replace(".json", "")

        base_params = load_parameters(latest_year).model_dump()

        transformed_data = transform_historical_record(relevant_record)

        # Merge the transformed data with the base parameters
        base_params.update(transformed_data)

        return Parameters.model_validate(base_params)
    else:
        raise FileNotFoundError(f"No historical data found for year {year_str}")
