# Source Code

This directory contains the core Python source code for the NZ Microsimulation Model.

## Contents:

*   `microsim.py`: Contains functions for income tax and related calculations (e.g., `taxit`, `calctax`, `netavg`, `calcietc`, `eitc`, `simrwt`, `supstd`).
*   `tax_calculator.py`: Convenience class that wraps core tax calculations and stores parameter sets.
*   `acc_levy.py`: Implements the ACC earner's levy and payroll deduction helpers.
*   `wff_microsim.py`: Implements the Working for Families (WFF) microsimulation model (`famsim`).
*   `rules_engine.py`: Lightweight engine for composing WFF policy rules.
*   `wff_microsim_main.py`: A script to run the WFF microsimulation model with sample data.
*   `payroll_deductions.py`: Helper functions for KiwiSaver contributions and student loan repayments.
*   `value_of_information.py`: Functions for computing the Expected Value of Perfect Information (EVPI) from probabilistic sensitivity analysis outputs.
*   `__init__.py`: Makes the `src` directory a Python package.
*   `py.typed`: Indicates that this package supports type checking.
