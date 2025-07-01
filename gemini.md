# NZ Microsimulation Model

This project is a Python-based microsimulation model for the New Zealand tax and transfer system. It is a translation of the SAS-based models provided by Inland Revenue.

## Project Goals

The primary goal of this project is to create a transparent, accessible, and extensible microsimulation model for New Zealand. This includes:

*   **Replicating Existing Functionality:** The initial focus is on replicating the functionality of the existing SAS models for income tax and Working for Families (WFF).
*   **Parameterization:** Where the original models use microdata, this project will use appropriate parameters and distributions to ensure the model is self-contained and does not require access to sensitive data.
*   **Testing and Documentation:** The project will include a comprehensive test suite to ensure the accuracy of the model and will be well-documented to facilitate understanding and use.
*   **Economic Analysis:** The project will include an economic analysis of the model and its outputs, presented in the style of an economics paper.

## Roadmap

The following is a high-level roadmap for the project:

1.  **Verify Translation & Functionality:** Check that the Python code correctly implements the logic from the original SAS macros and that all existing tests pass.
2.  **Document Code:** Add clear, comprehensive docstrings to the translated Python functions to explain their purpose, parameters, and return values.
3.  **Ongoing Maintenance and Improvement:** The project will be an ongoing effort, with continuous improvement of the model, documentation, and analysis.

## Future Roadmap

Once the current code is verified and documented, the project will explore adding additional functionality, such as:

*   **Update to Current Tax Policies:**
    *   Incorporate the 2024-2025 composite tax rates and thresholds.
    *   Update the In-Work Tax Credit (IWTC) entitlements.
    *   Adjust the Working for Families abatement thresholds.
    *   Incorporate the "FamilyBoost" childcare tax credit.
    *   Update the Independent Earner Tax Credit (IETC) eligibility and abatement rules.
*   **Implement a Longitudinal Framework:**
    *   Refactor the model to support analysis across different time periods.
    *   Adopt a flexible parameterization approach, such as using parameter files per year (e.g., `params_2022.json`, `params_2025.json`), to manage changes in tax laws over time.
*   **Behavioral Responses:** Incorporating behavioral responses to policy changes, such as changes in labor supply or savings behavior.
*   **Dynamic Simulation:** Extending the model to allow for dynamic simulation over time, including demographic and economic changes.
*   **Integration with Other Models:** Exploring the potential for integrating the model with other social policy models in New Zealand.

## Progress Log

*   **2025-06-30:**
    *   Recreated SAS files from PDF document.
    *   Established Python project structure.
    *   Moved original SAS model files to `sas_models/` directory.
    *   Translated the following SAS macros to Python:
        *   `taxit`
        *   `calctax`
        *   `netavg`
        *   `calcietc`
        *   `eitc`
        *   `simrwt`
        *   `supstd`
    *   Created unit tests for all translated functions.
    *   All tests are passing.
    *   Added instructions on how to run tests to `README.md`.
    *   Created `pyproject.toml` for centralized project configuration and dependency management.
    *   Migrated dependencies from `requirements.txt` to `pyproject.toml` and removed `requirements.txt`.
    *   Added `ruff` for linting and formatting, configured in `pyproject.toml`.
    *   Formatted and fixed linting issues using `ruff`.
    *   Added `pre-commit` hooks for automated linting and formatting before commits.
    *   Initialized Git repository and installed pre-commit hooks.
    *   Added `LICENSE` file (MIT License).
    *   Added `CONTRIBUTING.md` with contribution guidelines.
    *   Added `CITATION.cff` for citation information.
    *   Added `SECURITY.md` for vulnerability reporting.
    *   Organized documentation files into a `docs/` directory.
    *   Moved PDF documents to `docs/external/` for better organization.
    *   Added `CHANGELOG.md` to document project changes.
    *   Added `Makefile` to automate common development tasks.
    *   Updated `.gitignore` to include new directories and IDE-specific files.
    *   Updated `README.md` to reflect all new additions and organizational changes.
