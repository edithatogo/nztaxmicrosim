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


# The get_historical_parameters and transform_historical_record functions
# are now obsolete as all data is stored in and loaded from the SQLite database.
# The historical JSON file is also no longer the primary source of truth.
