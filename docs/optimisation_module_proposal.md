
# Proposal for an Optimisation Module

This document outlines a proposal for adding an optimisation module to the New Zealand tax microsimulation model. This exploration was prompted by the user's interest in finding optimal tax and transfer policies based on a set of defined objectives.

## 1. Problem Definition

The core idea is to create a module that can search for an "optimal" set of tax and transfer policy parameters. This requires defining:

*   **An Objective Function:** This is what we want to maximise or minimise. It could be a single objective or a combination of multiple objectives. Examples include:
    *   Maximising total tax revenue for the government.
    *   Minimising income inequality (e.g., as measured by the Gini coefficient).
    *   Maximising the average disposable income of households in the bottom quintile.
    *   A weighted combination of the above.

*   **Decision Variables:** These are the policy parameters that the optimisation module can change. Examples include:
    *   Income tax bracket thresholds.
    *   Income tax rates for each bracket.
    *   The amount of a specific tax credit (e.g., the Independent Earner Tax Credit).
    *   The abatement rate for a benefit.

*   **Constraints:** These are the rules that must be followed. Examples include:
    *   The total cost to the government cannot exceed a certain amount.
    *   Tax rates cannot be negative or exceed 100%.
    *   The order of tax brackets must be maintained.

The optimisation problem is then to find the set of decision variables that maximises (or minimises) the objective function, subject to the constraints.

## 2. Proposed Approach

We can think of this as a "black box" optimisation problem. The microsimulation model is the black box: we give it a set of policy parameters, and it gives us a set of outcomes (like total tax revenue and a Gini coefficient). We want to find the best set of inputs to this black box.

Given the complexity of the microsimulation model, the relationship between the policy parameters and the outcomes is likely to be non-linear, with many local optima. This means that traditional gradient-based optimisation methods may not be suitable.

A more promising approach is to use **metaheuristic optimisation algorithms**, such as:

*   **Genetic Algorithms (GAs):** These algorithms are inspired by the process of natural selection. They work with a "population" of candidate solutions (sets of policy parameters). In each generation, the best solutions are selected and "bred" to create a new generation of solutions. This process is repeated until a good solution is found. GAs are well-suited to this kind of problem because they can explore a large and complex search space without getting stuck in local optima.

*   **Simulated Annealing (SA):** This algorithm is inspired by the process of annealing in metallurgy. It starts with a random solution and then iteratively tries to improve it by making small random changes. It is more likely to accept changes that lead to a better solution, but it will sometimes accept changes that lead to a worse solution. This allows it to escape local optima.

*   **Particle Swarm Optimisation (PSO):** This algorithm is inspired by the social behaviour of birds flocking or fish schooling. It works with a "swarm" of particles, where each particle represents a candidate solution. The particles move through the search space, and their movement is influenced by their own best-known position and the best-known position of the entire swarm.

### High-Level Architecture

The optimisation module would work as follows:

1.  **Initialisation:** The user defines the objective function, the decision variables, and the constraints. The optimisation algorithm is initialised with a set of random candidate solutions.

2.  **Evaluation:** For each candidate solution (i.e., for each set of policy parameters), the optimisation module calls the microsimulation model to calculate the outcomes. The objective function is then evaluated for each candidate solution.

3.  **Selection and Variation:** The optimisation algorithm selects the best candidate solutions and uses them to generate a new set of candidate solutions.

4.  **Termination:** Steps 2 and 3 are repeated until a termination condition is met (e.g., a certain number of generations have been run, or the solution has not improved for a certain number of generations).

5.  **Output:** The best solution found is returned to the user.

## 3. Integration with the Microsimulation Model

The optimisation module would need to be able to:

*   **Modify the policy parameters:** This would likely involve creating a new set of parameter files for each candidate solution.
*   **Run the microsimulation model:** The module would need to call the main function of the microsimulation model and pass it the path to the parameter files.
*   **Read the output of the microsimulation model:** The module would need to read the output files of the microsimulation model to get the values of the outcomes needed to evaluate the objective function.

## 4. Challenges and Considerations

*   **Computational Cost:** Microsimulation models can be computationally expensive to run. Since an optimisation algorithm may need to run the model thousands of times, the computational cost can be a major challenge. It may be necessary to use a simplified version of the model for the optimisation, or to use parallel computing to speed up the process.

*   **Defining "Equity":** There are many different ways to measure equity (e.g., the Gini coefficient, the Palma ratio, the Theil index). The choice of equity measure will affect the results of the optimisation. It is important to choose a measure that is appropriate for the research question.

*   **Dynamic Microsimulation:** The current model has a placeholder for dynamic simulation. If the model were to become fully dynamic (i.e., if it were to model the behavioural responses of individuals to policy changes), the optimisation problem would become much more complex. It would be necessary to consider the long-term effects of policy changes, and the optimisation algorithm would need to be able to handle this.

*   **Model Accuracy:** The results of the optimisation are only as good as the underlying microsimulation model. It is important to ensure that the model is well-validated and that it accurately reflects the real world.

## 5. Next Steps

A good first step would be to develop a proof-of-concept implementation of an optimisation module. This could involve:

1.  **Choosing a simple objective function:** For example, maximising total tax revenue.
2.  **Choosing a small number of decision variables:** For example, the tax rates for the existing income tax brackets.
3.  **Implementing a simple optimisation algorithm:** For example, a basic genetic algorithm.
4.  **Integrating the optimisation module with the existing microsimulation model.**

This proof-of-concept would allow us to explore the feasibility of the proposed approach and to identify any potential challenges. It would also provide a foundation for developing a more sophisticated optimisation module in the future.

## 6. Existing Work

The idea of using optimisation with microsimulation models is not new. For example, the **Policy Simulation Library (PSL)** in the United States has a tool called `Tax-Brain` that allows users to explore the effects of different tax policies. While not a full optimisation tool, it provides a platform for "what-if" analysis that is a step in this direction.

There is also a body of academic literature on this topic. For example, a search for "tax policy optimisation using microsimulation" on Google Scholar will return a number of relevant papers. Reviewing this literature would be a valuable next step.

## 7. Choice of Tooling: Specialized vs. General-Purpose

A key implementation decision is whether to use a specialized library like the **Policy Simulation Library (PSL)** or a general-purpose optimization library like **Optuna**, **Hyperopt**, or **Scikit-optimize**.

For this project, the recommended approach is to use a **general-purpose optimization library**.

### Analysis

**General-Purpose Optimizers (e.g., Optuna)**

This approach involves creating a Python wrapper function around the existing microsimulation model. This function would accept a set of policy parameters, run the simulation, and return a single "objective score" to be maximized or minimized.

*   **Pros:**
    *   **High Flexibility:** Integrates directly with the existing codebase without requiring a major rewrite.
    *   **State-of-the-Art Algorithms:** Provides access to powerful and efficient optimization algorithms (e.g., Bayesian optimization, TPE) well-suited for complex problems.
    *   **Simplicity:** The integration is conceptually straightforward and avoids the need to learn a new, large-scale framework.

*   **Cons:**
    *   Requires writing some "boilerplate" code to connect the optimizer to the simulation (e.g., updating parameter files, parsing results).

**Specialized Libraries (e.g., PSL)**

*   **Pros:**
    *   **Domain-Specific:** Built specifically for policy simulation, potentially offering relevant tools and data structures.

*   **Cons:**
    *   **High Adoption Cost:** This is the critical drawback. PSL is heavily based on the US tax system. Adapting the existing New Zealand-specific model to fit PSL's framework would require a complete and costly re-engineering effort.
    *   **Lack of Flexibility:** The project would be constrained by the design decisions of the library, which may not be suitable for the nuances of the NZ system.

### Recommendation

Using a tool like **Optuna** is the clear winner. The cost of adapting the model to a specialized, US-centric library would be enormous and provide little benefit over a more flexible, general-purpose optimizer.

## 8. Recommended Libraries

Here is a comparison of recommended Python libraries for this task. The best choice depends on the specific needs of the optimization problem.

| Library | Key Strengths | Best For... |
| :--- | :--- | :--- |
| 1. **Optuna** | **Overall Winner.** Modern, very easy to use, powerful algorithms (TPE, CMA-ES), great visualization tools, and a large community. | Getting started quickly with a flexible and powerful tool that can handle a wide variety of optimization problems. |
| 2. **Scikit-optimize** | Specializes in **Bayesian Optimization**, which is highly efficient when each function call (i.e., each simulation run) is very slow and computationally expensive. | Problems where the simulation takes a long time to run, as it's designed to find a good solution in the fewest possible iterations. |
| 3. **SciPy (optimize)** | **Robust and Standard.** Part of the scientific Python stack, it includes powerful global optimization algorithms like `differential_evolution` that are very effective and require minimal configuration. | A solid, dependency-light solution. `differential_evolution` is a great general-purpose algorithm for global optimization. |

### Summary

*   **Start with Optuna:** Its intuitive API makes it very easy to set up an optimization "study".
*   **Consider `scikit-optimize` if runs are very slow:** Its sample efficiency is a major advantage for computationally expensive simulations.
*   **Use `scipy.optimize` for a classic, robust approach:** A great choice if you prefer to stick to the core scientific Python stack.

## 9. Staged Implementation Roadmap

This pragmatic, two-phase approach allows for incremental development. We start by building the essential "plumbing" with a simple grid search, then swap in a powerful optimizer once the foundation is proven.

### Phase 1: Simple Parameter Scanning Module (Grid Search)

The goal is to create the basic infrastructure for running the simulation with varying parameters and collecting the results.

1.  **Create a Wrapper Function:** Develop a core function (`run_simulation_with_params`) that:
    *   Accepts a dictionary of policy parameters.
    *   Temporarily modifies the relevant JSON parameter files.
    *   Calls the main microsimulation function.
    *   Parses the output to retrieve key metrics (e.g., total tax revenue, Gini coefficient).
    *   Returns these metrics.

2.  **Build the Grid Search Loop:**
    *   Create a script that defines a "grid" of parameters to test (e.g., a list of different tax rates).
    *   Loop through every combination of these parameters.
    *   For each combination, call the wrapper function and store the results.

3.  **Save Results:** After the loop completes, save the collected results (input parameters and their corresponding output metrics) to a CSV file for easy analysis.

### Phase 2: Advanced Optimization Module (e.g., Optuna)

This phase builds directly on the work from Phase 1 by replacing the simple grid search with an intelligent optimizer.

1.  **Adapt the Wrapper:** The `run_simulation_with_params` function from Phase 1 is adapted to become the `objective` function required by Optuna. It will be modified to return a single "score" to be optimized.

2.  **Create an Optuna "Study":**
    *   Define a broad search space for the policy parameters (e.g., a tax rate can be any float between 0.10 and 0.25).
    *   Create an Optuna study object.
    *   Pass the `objective` function to Optuna's `optimize` method.

3.  **Leverage Intelligent Optimization:** Optuna will intelligently call the objective function, efficiently searching the parameter space to find the optimal policy settings. This approach de-risks the project and ensures a working, useful tool is delivered at the end of Phase 1.
