# Dynamic Behavioural Extensions

The Policy Simulation Library now includes a module for simulating the dynamic behavioural responses of individuals to changes in the tax and benefit system. This initial implementation focuses on labour supply responses, driven by changes in Effective Marginal Tax Rates (EMTRs).

## Core Concepts

### Effective Marginal Tax Rate (EMTR)

The EMTR is a crucial metric for understanding work incentives. It represents the proportion of an additional dollar of earnings that is lost to either increased taxes or reduced benefits. A high EMTR can create a "poverty trap," where individuals have little financial incentive to increase their work hours or seek higher-paid employment.

The simulation calculates EMTRs for individuals by applying a small "shock" to their income (e.g., an extra $100 of earnings) and measuring the change in their net disposable income after taxes and benefits are recalculated.

**Formula:**
`EMTR = 1 - (Change in Net Disposable Income / Change in Gross Earnings)`

### Labour Supply Response

The labour supply response model uses the calculated EMTRs to predict how individuals might adjust their working hours. The model is based on economic principles of utility maximization, where individuals balance the trade-offs between labour (which generates income) and leisure.

The current implementation uses a simple elasticity-based model. When an individual's EMTR changes due to a policy reform, the model estimates a new desired number of work hours.

**Key features:**
- The response is probabilistic, meaning not everyone will adjust their hours.
- The magnitude of the change is influenced by a configurable elasticity parameter.
- The model can be toggled on or off in the dynamic simulation runner.

## Methodology and Implementation

The core logic is implemented in the `src/behavioural.py` module.

- `calculate_emtr()`: This function takes the core simulation function, a person's ID, and the baseline simulation results to calculate their EMTR. It works by creating a counterfactual scenario with a small income increase and comparing the outcomes.
- `labour_supply_response()`: This function takes the change in EMTR and an elasticity value to determine the percentage change in desired labour supply.

This functionality is integrated into the `run_dynamic_simulation` function, which will apply the behavioural adjustments in each year of the simulation if enabled.

## Example Usage

The following example demonstrates how to run a dynamic simulation with the behavioural response model enabled.

```python
# examples/run_dynamic_simulation_with_behaviour.py
import pandas as pd
from psl.core import run_dynamic_simulation
from psl.reforms import reform_2023
from psl.reforms.utils import get_reform_from_name
from psl.utils.data import get_data
import os

# Get the absolute path to the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Load the baseline input data
input_data_path = os.path.join(project_root, 'puf.csv')
input_data = pd.read_csv(input_data_path)

# Define simulation parameters
start_year = 2024
end_year = 2034
reform_name = "reform_2023"  # A hypothetical reform

# Get the reform function from its name
reform = get_reform_from_name(reform_name)

# Define a baseline simulation function (no reform)
def baseline_simulation_function(data, year):
    # In a real scenario, this would be a comprehensive tax/benefit calculation
    # For this example, we'll use a placeholder.
    # The actual calculations are in psl.core
    from psl.core import calculate_taxes_and_benefits
    return calculate_taxes_and_benefits(data, year)

# Define a reform simulation function
def reform_simulation_function(data, year):
    # The actual calculations are in psl.core, applying the reform
    from psl.core import calculate_taxes_and_benefits
    reformed_data = reform(data, year)
    return calculate_taxes_and_benefits(reformed_data, year)


print("Running dynamic simulation with behavioural responses...")
# Run the dynamic simulation with behavioural responses enabled
historical_results_with_behaviour = run_dynamic_simulation(
    input_data,
    start_year,
    end_year,
    baseline_simulation_function,
    reform_simulation_function,
    apply_behavioural_responses=True
)

print(f"Simulated {len(historical_results_with_behaviour)} years of data with behavioural responses.")
# You can now analyze the historical_results_with_behaviour DataFrame
# to see the impact of the reform over time, including behavioural effects.
# For example, let's look at the average hours worked in the final year.
final_year_results = historical_results_with_behaviour[historical_results_with_behaviour['year'] == end_year]
average_hours_worked = final_year_results['hours_worked'].mean()

print(f"Average hours worked in {end_year} (with reform and behavioural response): {average_hours_worked:.2f}")

print("\nRunning dynamic simulation WITHOUT behavioural responses for comparison...")
# Run the dynamic simulation again without behavioural responses
historical_results_without_behaviour = run_dynamic_simulation(
    input_data,
    start_year,
    end_year,
    baseline_simulation_function,
    reform_simulation_function,
    apply_behavioural_responses=False
)
final_year_results_no_behaviour = historical_results_without_behaviour[historical_results_without_behaviour['year'] == end_year]
average_hours_worked_no_behaviour = final_year_results_no_behaviour['hours_worked'].mean()
print(f"Average hours worked in {end_year} (with reform but no behavioural response): {average_hours_worked_no_behaviour:.2f}")

```

## Limitations

- **Simplified Model:** The current labour supply model is a simplification of complex human behaviour. It does not account for non-financial factors, fixed work contracts, childcare constraints, or other real-world frictions.
- **Elasticity Assumption:** The results are highly sensitive to the chosen elasticity parameter. The default value is an estimate, and the true elasticity can vary significantly across different population subgroups.
- **Focus on Hours Worked:** The model only adjusts the quantity of labour (hours worked) and does not currently simulate changes in job type, career progression, or human capital investment.

Future work will focus on refining this model to incorporate more sophisticated behavioural dynamics.
