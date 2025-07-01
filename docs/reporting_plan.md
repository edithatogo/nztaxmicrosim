# Comprehensive Reporting Plan for NZ Microsimulation Model

This document outlines a comprehensive reporting strategy for the New Zealand Microsimulation Model, focusing on tables and plots to analyze both input (synthetic population) and output (calculated WFF entitlements) data. The aim is to provide clear insights into the model's behavior and the impact of policy simulations.

## I. Input Data Characteristics (Synthetic Population)

**Purpose:** To understand the demographic and economic profile of the synthetic population being simulated, ensuring the input data is representative and well-understood.

### Tables:

*   **Summary Statistics Table:**
    *   **Variables:** `familyinc`, `age`, `num_children`, `pplcnt`.
    *   **Metrics:** Mean, Median, Standard Deviation, Minimum, Maximum, 25th Percentile (Q1), 75th Percentile (Q3).
    *   **Format:** A table with variables as rows and metrics as columns.

*   **Frequency Distributions Table:**
    *   **Variables:** `num_children`, `adults`.
    *   **Metrics:** Counts and percentages for each unique value.
    *   **Format:** Separate tables for each variable, showing value, count, and percentage.

### Plots:

*   **Histograms/Density Plots:**
    *   **Variables:** `familyinc`, `age`.
    *   **Purpose:** Visualize the distribution of these continuous numerical variables.
    *   **Format:** Separate plots for each variable, showing frequency or density.

*   **Bar Charts:**
    *   **Variables:** `num_children`, `adults`.
    *   **Purpose:** Show the distribution of family types or household compositions.
    *   **Format:** Separate bar charts for each variable, with counts on the y-axis.

## II. Output Data Characteristics (Calculated Entitlements)

**Purpose:** To understand the distribution, magnitude, and overall impact of the calculated tax credits and other model outputs.

### Tables:

*   **Summary Statistics Table:**
    *   **Variables:** `FTCcalc`, `IWTCcalc`, `BSTCcalc`, `MFTCcalc`, `familyinc_grossed_up`, `abate_amt`, `BSTCabate_amt`.
    *   **Metrics:** Mean, Median, Standard Deviation, Minimum, Maximum, 25th Percentile (Q1), 75th Percentile (Q3).
    *   **Format:** A table with variables as rows and metrics as columns.

*   **Total Entitlements Table:**
    *   **Variables:** `FTCcalc`, `IWTCcalc`, `BSTCcalc`, `MFTCcalc`.
    *   **Metrics:** Sum of each calculated tax credit across the entire population.
    *   **Format:** A simple table showing the total amount for each credit.

### Plots:

*   **Histograms/Density Plots:**
    *   **Variables:** `FTCcalc`, `IWTCcalc`, `BSTCcalc`, `MFTCcalc`.
    *   **Purpose:** Visualize the distribution of calculated entitlements.
    *   **Format:** Separate plots for each variable.

*   **Box Plots:**
    *   **Variables:** `FTCcalc`, `IWTCcalc`, `BSTCcalc`, `MFTCcalc`.
    *   **Grouping:** By `num_children` or `pplcnt` (e.g., separate box plots for families with 0, 1, 2, 3+ children).
    *   **Purpose:** Compare the distribution of entitlements across different demographic groups.
    *   **Format:** Box plots showing quartiles and outliers for each group.

## III. Income Tax and Net Income Analysis

**Purpose:** To analyze the calculated income tax, net income, and effective tax rates across the population.

### Tables:

*   **Summary Statistics Table (Income Tax & Net Income):**
    *   **Variables:** `income_tax_payable`, `net_income`.
    *   **Metrics:** Mean, Median, Standard Deviation, Minimum, Maximum, 25th Percentile (Q1), 75th Percentile (Q3).
    *   **Format:** A table with variables as rows and metrics as columns.

*   **Effective Tax Rate by Income Quintile:**
    *   **Variables:** `income` (categorized into quintiles) vs. average effective tax rate (`income_tax_payable` / `income`).
    *   **Metrics:** Average effective tax rate for each income quintile.
    *   **Format:** A table with income quintiles as rows and average effective tax rate as a column.

### Plots:

*   **Histograms/Density Plots:**
    *   **Variables:** `income_tax_payable`, `net_income`.
    *   **Purpose:** Visualize the distribution of calculated income tax and net income.
    *   **Format:** Separate plots for each variable.

*   **Scatter Plot: Income Tax Payable vs. Income:**
    *   **X-axis:** `income`.
    *   **Y-axis:** `income_tax_payable`.
    *   **Purpose:** Illustrate the progressive nature of the income tax system.
    *   **Enhancements:** Potentially add lines representing tax brackets.
    *   **Format:** Scatter plot with individual data points.

## IV. Impact Analysis and Relationships

**Purpose:** To analyze how changes in input variables (especially income) affect the calculated entitlements, and to visualize the abatement process and other key relationships.

### Tables:

*   **Cross-Tabulations (Average Entitlements by Income Quintile):**
    *   **Variables:** `familyinc_grossed_up` (categorized into quintiles) vs. `FTCcalc`, `IWTCcalc`, `BSTCcalc`, `MFTCcalc`.
    *   **Metrics:** Average entitlement for each credit within each income quintile.
    *   **Format:** A table with income quintiles as rows and average entitlements as columns.

### Plots:

*   **Scatter Plots with Abatement Visualization:**
    *   **X-axis:** `familyinc_grossed_up`.
    *   **Y-axis:** `FTCcalc`, `IWTCcalc`, `BSTCcalc`, `MFTCcalc` (separate plots for each).
    *   **Purpose:** Show the relationship between family income and calculated entitlements, clearly illustrating the abatement thresholds and rates.
    *   **Enhancements:** Add vertical lines or shaded regions to indicate `abatethresh1`, `abatethresh2`, and `bstcthresh`.
    *   **Format:** Scatter plots with individual data points, potentially with a smoothed line or regression line.

## V. Equity and Distributive Analysis

**Purpose:** To provide a comprehensive analysis of the model's overall impact on income inequality, using standard economic metrics and visualizations.

### Tables:

*   **Gini Coefficient Analysis:**
    *   **Metrics:** Gini coefficient for:
        1.  Market Income (`income`).
        2.  Net Disposable Income (`income` + `total_wff_entitlement` - `income_tax_payable`).
    *   **Purpose:** Quantify the redistributive impact of the tax and transfer system.
    *   **Format:** A simple table showing the Gini coefficient before and after government intervention.

### Plots:

*   **Lorenz Curves:**
    *   **Variables:** Cumulative share of population vs. cumulative share of income for both Market Income and Net Disposable Income.
    *   **Purpose:** Graphically illustrate the reduction in income inequality.
    *   **Enhancements:** Include a "Line of Perfect Equality" for reference.
    *   **Format:** A single plot showing both Lorenz curves.

## VI. Reporting Tools

*   **Python Libraries:**
    *   `pandas`: For data loading, manipulation, and generating summary tables.
    *   `matplotlib.pyplot`: For creating a wide range of static plots.
    *   `seaborn`: For enhanced statistical graphics and aesthetically pleasing plots.

All plots will be saved as PNG image files in a dedicated `examples/reports` directory. Summary tables will be printed to the console or saved as text files if requested.
