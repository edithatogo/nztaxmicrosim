import json
<<<<<<< HEAD
import re
from pathlib import Path

=======
import os
from pathlib import Path
import re
>>>>>>> origin/update-a-bunch-of-stuff-5

def get_parameter_files(src_dir: Path) -> list[Path]:
    """Finds all parameter files in the src directory."""
    return sorted(src_dir.glob("parameters_*.json"))

<<<<<<< HEAD

=======
>>>>>>> origin/update-a-bunch-of-stuff-5
def get_all_rules(param_files: list[Path]) -> list[str]:
    """Gets a unique, sorted list of all rules from all parameter files."""
    all_rules = set()
    for file in param_files:
        with open(file, "r") as f:
            data = json.load(f)
            all_rules.update(data.keys())
    # These are not rules, so remove them.
    if "year" in all_rules:
        all_rules.remove("year")
    if "description" in all_rules:
        all_rules.remove("description")
    return sorted(list(all_rules))

<<<<<<< HEAD

=======
>>>>>>> origin/update-a-bunch-of-stuff-5
def generate_coverage_matrix(param_data: dict, all_rules: list[str]) -> str:
    """Generates a Markdown table for rule coverage."""
    header = "| Year | " + " | ".join(f"`{rule}`" for rule in all_rules) + " |"
    separator = "| --- |" + " :---: |" * len(all_rules)

    rows = []
    for year, data in param_data.items():
        row = f"| {year} |"
        for rule in all_rules:
            row += " ✅ |" if rule in data else " ❌ |"
        rows.append(row)

    return "\n".join([header, separator] + rows)

<<<<<<< HEAD

=======
>>>>>>> origin/update-a-bunch-of-stuff-5
def generate_detailed_tables(param_data: dict) -> str:
    """Generates detailed Markdown tables for each year's parameters."""
    detailed_docs = []
    for year, data in param_data.items():
        detailed_docs.append(f"## {year}\n")
        for rule, params in data.items():
            if rule in ["year", "description"]:
                continue
            detailed_docs.append(f"### `{rule}`\n")
            if isinstance(params, dict):
                header = "| Parameter | Value |\n| --- | --- |"
                rows = [f"| `{key}` | `{value}` |" for key, value in params.items()]
                detailed_docs.append(header + "\n" + "\n".join(rows))
            else:
                detailed_docs.append(f"`{params}`")
            detailed_docs.append("\n")
    return "\n".join(detailed_docs)


def generate_docs():
    """
    Generates documentation for the parameter files.
    """
    print("Generating parameter documentation...")

    # Correctly locate the root directory of the project
    root_dir = Path(__file__).parent.parent
    src_dir = root_dir / "src"
    docs_dir = root_dir / "docs"
    output_file = docs_dir / "parameter_coverage.md"

    param_files = get_parameter_files(src_dir)

    param_data = {}
    year_pattern = re.compile(r"parameters_(\d{4}-\d{4})\.json")

    for file in param_files:
<<<<<<< HEAD
        print(f"Processing file: {file.name}")  # Added for debugging
=======
        print(f"Processing file: {file.name}") # Added for debugging
>>>>>>> origin/update-a-bunch-of-stuff-5
        match = year_pattern.search(file.name)
        if match:
            year = match.group(1)
            with open(file, "r") as f:
                param_data[year] = json.load(f)

    # Sort data by year
    param_data = dict(sorted(param_data.items()))

    all_rules = get_all_rules(param_files)

    # Generate the content
    title = "# Parameter Coverage\n\n"
<<<<<<< HEAD
    intro = (
        "This page automatically documents the coverage of policy rules across "
        "different years, based on the available parameter files.\n\n"
    )
=======
    intro = "This page automatically documents the coverage of policy rules across different years, based on the available parameter files.\n\n"
>>>>>>> origin/update-a-bunch-of-stuff-5

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

<<<<<<< HEAD

=======
>>>>>>> origin/update-a-bunch-of-stuff-5
if __name__ == "__main__":
    generate_docs()
