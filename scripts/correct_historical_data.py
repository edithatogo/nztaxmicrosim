import os
import sqlite3

# Define the known start years for each policy
POLICY_START_YEARS = {
    "acc_levy": 1974,
    "wff": 2005,
    "ietc": 2009,
    "kiwisaver": 2007,
    "accommodation_supplement": 1996,
}

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "data", "parameters.db")


def correct_historical_data():
    """
    Corrects the historical parameter data in the SQLite database by finding
    gaps and filling them with the parameters from the most recent previous year.
    """
    print("Starting historical data correction...")

    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get the overall range of years in the database
    cursor.execute("SELECT MIN(year), MAX(year) FROM policy_parameters")
    min_db_year, max_db_year = cursor.fetchone()

    for policy_key, start_year in POLICY_START_YEARS.items():
        print(f"\nProcessing policy: '{policy_key}' (starts in {start_year})")

        # Get all existing data for this policy, ordered by year
        cursor.execute(
            (
                "SELECT year, parameters FROM policy_parameters "
                "WHERE policy_key = ? AND parameters IS NOT NULL "
                "ORDER BY year ASC"
            ),
            (policy_key,),
        )
        existing_data = {year: params for year, params in cursor.fetchall()}

        if not existing_data:
            print("  Warning: No data found for this policy. Skipping.")
            continue

        last_known_params = None

        # Iterate through all years from the policy's start year to the max year in the DB
        for year_to_check in range(start_year, max_db_year + 1):
            if year_to_check in existing_data:
                # Data exists and is not null, so it's our new baseline
                last_known_params = existing_data[year_to_check]
                # print(f"  - Data found for {year_to_check}. Setting as new baseline.")
            else:
                # This year is missing data. We need to fill it.
                if last_known_params is None:
                    # This should not happen if the start_year is correct and there's any data at all
                    print(f"  ERROR: Cannot fill {year_to_check} as no previous data has been found.")
                else:
                    # Check if a row exists but is null, or if it doesn't exist at all
                    cursor.execute(
                        "SELECT rowid FROM policy_parameters WHERE year = ? AND policy_key = ?",
                        (year_to_check, policy_key),
                    )
                    row = cursor.fetchone()
                    if row:
                        print(f"  - Updating NULL data for {year_to_check}...")
                        cursor.execute(
                            "UPDATE policy_parameters SET parameters = ? WHERE year = ? AND policy_key = ?",
                            (last_known_params, year_to_check, policy_key),
                        )
                    else:
                        print(f"  - Inserting MISSING data for {year_to_check}...")
                        cursor.execute(
                            "INSERT INTO policy_parameters (year, policy_key, parameters) VALUES (?, ?, ?)",
                            (year_to_check, policy_key, last_known_params),
                        )

    conn.commit()
    conn.close()

    print("\nData correction finished.")


if __name__ == "__main__":
    correct_historical_data()
