import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "data", "parameters.db")


def debug_db():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT year, parameters FROM policy_parameters WHERE policy_key = 'accommodation_supplement' ORDER BY year;"
    )
    rows = cursor.fetchall()

    print("Data for 'accommodation_supplement':")
    for year, params in rows:
        status = "Data" if params is not None else "Null"
        print(f"- {year}: {status}")

    conn.close()


if __name__ == "__main__":
    debug_db()
