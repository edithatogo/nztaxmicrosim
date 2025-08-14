# Dynamic Simulation with Behavioural Response

The `src.dynamic_simulation` module provides a framework for running multi-year simulations that can optionally account for behavioural responses to policy changes. This allows for a more realistic analysis of the long-term impacts of reforms.

The primary behavioural response modelled is **labour supply**, where individuals may choose to work more or fewer hours in response to changes in their financial incentives.

## Methodology

The labour supply model is based on standard microeconomic theory. The key drivers are:

1.  **Effective Marginal Tax Rate (EMTR):** This is the rate at which an individual loses their next dollar of earned income to either increased taxes or reduced benefit payments. A higher EMTR reduces the incentive to work an additional hour. The model includes a robust `calculate_emtr` function to determine this for each individual.
2.  **Labour Supply Elasticity:** This parameter, drawn from economic literature, measures how responsive an individual's labour supply (hours worked) is to a change in their net wage rate. The model can use different elasticities for different demographic groups (e.g., primary vs. secondary earners).

When the behavioural response is enabled, the simulation performs these steps for each year:
1.  Calculates the tax and benefit outcomes of a policy reform for a static population.
2.  Compares the EMTR and net income before and after the reform.
3.  Uses the change in EMTR and the relevant elasticity to calculate a percentage change in labour supply for each individual.
4.  Adjusts each individual's labour income based on this response.
5.  This new, behaviourally-adjusted population is then used as the input for the following simulation year.

## Key Functions

### `run_dynamic_simulation()`

This is the main function for running a multi-year simulation.

::: src.dynamic_simulation.run_dynamic_simulation

### `labour_supply_response()`

This is the core function that calculates the change in labour supply.

::: src.behavioural.labour_supply_response

## Current Limitations

*   The model currently only simulates the **intensive margin** of labour supply (i.e., changes in hours for those already working). It does not model the **extensive margin** (i.e., decisions to enter or leave the workforce).
*   The elasticity parameters used are placeholders and should be updated with values from specific, relevant research for accurate modelling.

## Usage Example

A full, working example of how to run a dynamic simulation with behavioural response can be found in the `examples/run_dynamic_simulation_with_behaviour.py` script. The key is to set `use_behavioural_response=True` and provide a dictionary of `elasticity_params` when calling `run_dynamic_simulation`.
