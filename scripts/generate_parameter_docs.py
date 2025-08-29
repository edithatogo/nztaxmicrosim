import json
import sqlite3
from collections import defaultdict
from pathlib import Path


def get_params_from_db(db_path: Path) -> dict:
    """Fetches all parameters from the SQLite database."""
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found at {db_path}")

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT year, policy_key, parameters FROM policy_parameters ORDER BY year")
    rows = cursor.fetchall()
    conn.close()

    # Reshape data into a nested dictionary: {year: {policy: params}}
    param_data = defaultdict(dict)
    for year, policy_key, params_json in rows:
        # Create a proper year string
        year_str = f"{year}-{year + 1}"
        if params_json:
            param_data[year_str][policy_key] = json.loads(params_json)
        else:
            param_data[year_str][policy_key] = {}  # Handle cases where params are null

    return dict(sorted(param_data.items()))


def get_all_rules(param_data: dict) -> list[str]:
    """Gets a unique, sorted list of all rules from the parameter data."""
    all_rules = set()
    for year_data in param_data.values():
        all_rules.update(year_data.keys())

    # These are not rules, so remove them.
    if "_source_references" in all_rules:
        all_rules.remove("_source_references")

    return sorted(list(all_rules))


def generate_coverage_matrix(param_data: dict, all_rules: list[str]) -> str:
    """Generates a Markdown table for rule coverage."""
    header = "| Year | " + " | ".join(f"`{rule}`" for rule in all_rules) + " |"
    separator = "| --- |" + " :---: |" * len(all_rules)

    rows = []
    for year, data in param_data.items():
        row = f"| {year} |"
        for rule in all_rules:
            row += " ✅ |" if rule in data and data[rule] else " ❌ |"
        rows.append(row)

    return "\n".join([header, separator] + rows)


def generate_detailed_tables(param_data: dict) -> str:
    """Generates detailed Markdown tables for each year's parameters."""
    detailed_docs = []
    for year, data in param_data.items():
        detailed_docs.append(f"## {year}\n")
        # Sort rules alphabetically for consistent output
        sorted_rules = sorted(data.keys())
        for rule in sorted_rules:
            params = data[rule]
            detailed_docs.append(f"### `{rule}`\n")
            if isinstance(params, dict) and params:
                header = "| Parameter | Value |\n| --- | --- |"
                rows = [f"| `{key}` | `{json.dumps(value)}` |" for key, value in sorted(params.items())]
                detailed_docs.append(header + "\n" + "\n".join(rows))
            elif params:
                detailed_docs.append(f"`{params}`")
            else:
                detailed_docs.append("*No parameters for this rule.*")
            detailed_docs.append("\n")
    return "\n".join(detailed_docs)


def generate_docs():
    """
    Generates documentation for the parameter files.
    """
    print("Generating parameter documentation from SQLite database...")

    root_dir = Path(__file__).parent.parent
    db_path = root_dir / "src" / "data" / "parameters.db"
    output_file = root_dir / "docs" / "parameter_coverage.md"

    param_data = get_params_from_db(db_path)
    all_rules = get_all_rules(param_data)

    # Generate the content
    title = "# Parameter Coverage\n\n"
    intro = (
        "This page automatically documents the coverage of policy rules across "
        "different years, based on the available parameter files.\n\n"
    )

    matrix_title = "## Rule Coverage Matrix\n\n"
    matrix = generate_coverage_matrix(param_data, all_rules)

    details_title = "\n\n## Detailed Parameters by Year\n"
    details = generate_detailed_tables(param_data)

    # Write to the output file
    with open(output_file, "w") as f:
        f.write(title)
        f.write(intro)
        f.write(matrix_title)
        f.write(matrix)
        f.write(details_title)
        f.write(details)

    print(f"Documentation generated successfully at {output_file}")


if __name__ == "__main__":
    generate_docs()
