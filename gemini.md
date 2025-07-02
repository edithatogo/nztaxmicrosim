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
2.  **Document Code:** Added clear, comprehensive docstrings to the translated Python functions to explain their purpose, parameters, and return values. (Completed 2025-07-02)
3.  **Ongoing Maintenance and Improvement:** The project will be an ongoing effort, with continuous improvement of the model, documentation, and analysis.

## Future Roadmap

Once the current code is verified and documented, the project will explore adding additional functionality, such as:

*   **Implement a Longitudinal Framework:**
    *   Refactor the model to support analysis across different time periods.
    *   Adopt a flexible parameterization approach, such as using parameter files per year (e.g., `params_2022.json`, `params_2025.json`), to manage changes in tax laws over time.
*   **Behavioral Responses:** Incorporating behavioral responses to policy changes, such as changes in labor supply or savings behavior.
*   **Dynamic Simulation:** Extending the model to allow for dynamic simulation over time, including demographic and economic changes.
*   **Integration with Other Models:** Exploring the potential for integrating the model with other social policy models in New Zealand.
*   **Economic Analysis:** The project will include an economic analysis of the model and its outputs, presented in the style of an economics paper.

## Progress Log

*   **2025-07-02:**
    *   Parameterized the microsimulation model to allow for easy updates and comparisons between different tax years.
    *   Added historical tax rules for the years 2016-2021.
    *   Updated the model with the 2024-2025 composite tax rates, IETC, and IWTC changes.
    *   Added a new function for the FamilyBoost tax credit.
    *   Updated tests to use the new parameter system and verify the new rules.
    *   Updated examples/basic_usage.py to demonstrate the new system.
    *   Updated README.md to document the parameterization feature.
