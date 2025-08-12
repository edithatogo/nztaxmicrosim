# Demographic Modelling

The `src.demographic_modelling` module provides tools to simulate demographic changes in a population over time. This is a key part of the "Historical Analysis Enhancements" outlined in the project roadmap.

The initial version of this module focuses on two key aspects of demographic change:
1.  **Aging:** All individuals in the population are aged forward by one year.
2.  **Fertility:** New individuals (babies) are added to the population based on age-specific fertility rates.

## Key Functions

### `age_population_forward()`

This is the main function for performing the demographic simulation for a single year.

::: src.demographic_modelling.age_population_forward

## Data Source for Fertility Rates

The simulation of births relies on age-specific fertility rates. The `get_fertility_data()` function currently loads this data from a placeholder file: `src/data/fertility_rates.json`.

**Important:** The data in this file is for demonstration purposes only and is not based on real, comprehensive historical data. For accurate research, this data should be replaced with official data from a source like [Stats NZ Infoshare](http://infoshare.stats.govt.nz/).

## Current Limitations & Future Work

This is the first version of the demographic modelling module and has several limitations that could be addressed in future work:

*   **Mortality:** The model does not yet simulate deaths.
*   **Family Formation:** The model only adds children to existing families; it does not simulate the formation of new family units.
*   **Migration:** The model does not account for immigration or emigration.
*   **Data:** The underlying fertility data is a placeholder.

## Usage Example

A full, working example of how to use this functionality can be found in the `examples/run_demographic_simulation.py` script. The basic process is to load a population DataFrame for a given year and pass it to the `age_population_forward()` function to get the population for the next year.

```python
# Example snippet from examples/run_demographic_simulation.py

population_1991 = age_population_forward(
    df=population_1990,
    year=1990
)
```
