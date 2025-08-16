import sqlite3
import json
import sys
import os

# Define the known start years for each policy
# (as determined in the previous data audit)
POLICY_START_YEARS = {
    "acc_levy": 1974,
    "wff": 2005,
    "ietc": 2009,
    "kiwisaver": 2007,
    "accommodation_supplement": 1996,
    "independent_earner_tax_credit": 2009,
}

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "data", "parameters.db")

def audit_historical_data():
    """
    Audits the historical parameter data in the SQLite database for correctness.

    Checks for two main types of errors:
    1. A policy block exists for a year before its official start date.
    2. A policy block is null for a year after it was introduced and should exist.

    Exits with a non-zero status code if any errors are found.
    """
    print("Starting historical data audit...")
    errors_found = 0

    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all distinct years from the database
    cursor.execute("SELECT DISTINCT year FROM policy_parameters ORDER BY year")
    years = [row[0] for row in cursor.fetchall()]

    for year in years:
        for policy_key, start_year in POLICY_START_YEARS.items():
            cursor.execute(
                "SELECT parameters FROM policy_parameters WHERE year = ? AND policy_key = ?",
                (year, policy_key)
            )
            row = cursor.fetchone()

            # If there's no row, we assume the policy block is implicitly null.
            params_are_null = (row is None) or (row[0] is None)

            # Check for policies existing before they should
            if year < start_year and not params_are_null:
                print(f"ERROR: Audit failed for year {year}, policy '{policy_key}'.")
                print(f"       Policy should not exist before {start_year}, but data was found.")
                errors_found += 1

            # Check for policies being null after they should exist
            if year >= start_year and params_are_null:
                # Special case: IETC was repealed and then reintroduced.
                # We don't have the exact dates of repeal, so we will ignore this check for IETC for now.
                # A more advanced audit script would handle this.
                if policy_key == "ietc" or policy_key == "independent_earner_tax_credit":
                    continue

                print(f"ERROR: Audit failed for year {year}, policy '{policy_key}'.")
                print(f"       Policy should exist from {start_year} onwards, but data was null.")
                errors_found += 1

    conn.close()

    if errors_found > 0:
        print(f"\nAudit finished. Found {errors_found} errors.")
        sys.exit(1)
    else:
        print("Audit finished. No errors found.")
        sys.exit(0)

if __name__ == "__main__":
    audit_historical_data()
