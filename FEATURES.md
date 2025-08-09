# Features of the NZ Tax Microsimulation Model

This document provides a comprehensive overview of the features included in the NZ Tax Microsimulation Model.

## Core Tax and Benefit Calculations

The model implements a wide range of New Zealand's tax and benefit rules.

### Income Tax

- **Progressive Income Tax:** Calculates income tax based on a system of progressive tax brackets.
- **Independent Earner Tax Credit (IETC):** Calculates the IETC for eligible individuals.
- **Resident Withholding Tax (RWT):** Calculates RWT on interest income.

### Levies

- **ACC Earner's Levy:** Calculates the ACC levy on earnings up to a specified maximum.

### Working for Families (WFF)

The model includes a detailed implementation of the WFF tax credits:

- **Family Tax Credit (FTC):** Calculated based on family income and the number of children.
- **In-Work Tax Credit (IWTC):** For working families, with eligibility based on hours worked.
- **Best Start Tax Credit (BSTC):** For families with young children.
- **Minimum Family Tax Credit (MFTC):** A top-up for working families to ensure they are better off than on a benefit.

The WFF calculations account for:

- **Income Abatement:** Reduction of credits based on family income.
- **Shared Care:** Adjustments to entitlements when care of children is shared.
- **Calibrations:** Adjustments to better match real-world data.

### Main Benefits

The model calculates entitlements for the following main benefits:

- **Jobseeker Support (JSS):** For people who are looking for work or are unable to work due to a health condition.
- **Sole Parent Support (SPS):** For single parents with dependent children.
- **Supported Living Payment (SLP):** For people with a significant health condition, injury, or disability.

### Other Assistance

- **Accommodation Supplement:** Helps with rent, board, or mortgage payments.
- **Winter Energy Payment (WEP):** Helps with heating costs during winter.
- **NZ Superannuation:** The model can factor in NZ Superannuation receipt for other calculations (e.g., IETC eligibility).

### Payroll Deductions

- **KiwiSaver:** Calculates employee contributions to the KiwiSaver retirement savings scheme.
- **Student Loan Repayments:** Calculates mandatory student loan repayments for those with income above the threshold.

## Simulation and Modelling

### Simulation Engine

- **Modular Pipeline:** The simulation is structured as a pipeline of independent rules that can be enabled, disabled, or reordered. This allows for flexible policy analysis.
- **Static and Dynamic Simulation:** The model supports both single-year (static) and multi-year (dynamic) simulations.
- **Parameterisation:** Policy rules are defined in JSON files for each tax year, allowing for easy modification and historical analysis.

### Historical Data

- **Extensive Coverage:** The model includes parameterised policy rules from 2005 to 2025.
- **Historical Fallback:** The model can automatically fall back to historical data for years outside the main parameterised range.

### Population Data

- **Synthetic Population:** The repository includes tools to generate a synthetic population for use in simulations.

## Analysis and Reporting

- **Reporting Framework:** A framework for generating reports on simulation results.
- **Sensitivity Analysis:** Tools for conducting sensitivity analysis on the model's parameters.
- **Value of Information (VOI):** Includes tools for VOI analysis, such as calculating the Expected Value of Perfect Information (EVPI).
- **Validation:** Tools for validating the model's outputs against known results.
- **Budget Analysis:** Tools for analysing the fiscal impact of policy changes.

## Development and Extensibility

- **Open Source:** The model is open source under the Apache 2.0 license.
- **Testing:** A comprehensive test suite is included to ensure the accuracy of the calculations.
- **Extensible:** The modular design of the model makes it easy to add new rules and features.
