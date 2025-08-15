import sqlite3
import json
import os
import re

def migrate_parameters_to_db():
    """
    Reads all parameters_YYYY-YYYY.json files from the src/ directory,
    and populates a new SQLite database with the data.
    """
    db_path = "src/data/parameters.db"
    src_dir = "src/"

    # Remove existing database file if it exists
    if os.path.exists(db_path):
        os.remove(db_path)

    # Connect to the database and create the table
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE policy_parameters (
        year INTEGER,
        policy_key TEXT,
        parameters TEXT,
        PRIMARY KEY (year, policy_key)
    )
    """)

    print(f"Database created at {db_path}")

    # Find, read, and migrate parameter files
    param_file_pattern = re.compile(r"parameters_(\d{4})-\d{4}\.json")

    for filename in sorted(os.listdir(src_dir)):
        match = param_file_pattern.match(filename)
        if match:
            year = int(match.group(1))
            filepath = os.path.join(src_dir, filename)

            print(f"Migrating {filename}...")

            with open(filepath, 'r') as f:
                data = json.load(f)

            for key, value in data.items():
                if key == "_source_references":
                    continue

                # Convert the parameter object to a JSON string for storage
                params_json = json.dumps(value) if value is not None else None

                cursor.execute(
                    "INSERT INTO policy_parameters (year, policy_key, parameters) VALUES (?, ?, ?)",
                    (year, key, params_json)
                )

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    print("Migration complete. All parameter files have been migrated to the database.")

if __name__ == "__main__":
    migrate_parameters_to_db()
