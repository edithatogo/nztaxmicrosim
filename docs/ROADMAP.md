# Roadmap

This document outlines development priorities for the NZ Microsimulation Model, which aims to assess New Zealand tax settings through static and dynamic analysis of budget impact, personal income outcomes, equity, and value-of-information.

## Upcoming Tasks

1. **Core Static Personal Income Model** ✅
   - *Milestone:* Finalize baseline calculations for individual liabilities and incomes.
   - *Priority:* **High**
   - *Status:* **Done**

2. **Expand Rule Coverage** ✅
   - *Milestone:* Implement additional personal tax, benefit, and levy rules.
   - *Tasks:*
     - Child Support payments ✅
     - Disability Allowance ✅
     - Taxation of investment income (e.g., PIE funds) ✅
     - Tax credits for charitable donations ✅
   - *Priority:* **High**
   - *Status:* **Done**.

3. **Modular Simulation Pipeline** ✅
   - *Milestone:* Design plug-in architecture for tax and benefit rules.
   - *Priority:* **High**
   - *Status:* **Done**

4. **Dynamic Behavioural Extensions** *(In Progress)*
   - *Milestone:* Introduce modules that capture behavioural responses and longitudinal impacts of policy changes.
   - *Priority:* **Medium**
   - *Status:* **In Progress**. A simple dynamic simulation utility exists.

5. **Complete Sensitivity Analysis Tools** ✅
   - *Milestone:* Finalize parameter sweep utilities and integrate with scenario management.
   - *Priority:* **Medium**
   - *Status:* **Done**

6. **Budget Impact Modules** ✅
   - *Milestone:* Build routines to aggregate fiscal costs and savings across scenarios.
   - *Priority:* **High**
   - *Status:* **Done**

7. **Expanded Equity Metrics** ✅
   - *Milestone:* Introduce additional indicators of distributional effects (e.g., progressivity indexes).
   - *Priority:* **Medium**
   - *Status:* **Done**

8. **Value-of-Information Analysis** ✅
   - *Milestone:* Add module for assessing the benefit of additional data sources or improved data quality.
   - *Priority:* **Medium**
   - *Status:* **Done**

## Short-Term Milestones

- **Q3 2025:** Deliver the completed static personal income model and begin work on dynamic behavioural extensions.
- **Q4 2025:** Release budget impact functionality alongside the first round of new equity metrics and value-of-information analysis.

## Future Features

9. **Policy Optimisation Module**
    - *Description:* Introduce a module to search for optimal policy parameters based on user-defined objectives (e.g., maximizing revenue while minimizing inequality).
    - *Priority:* **Low**
    - *Status:* **In Progress**
    - *Implementation Plan:*
      - **Phase 1: Simple Parameter Scanning:** Develop the core infrastructure to programmatically run the simulation with a grid of different input parameters and save the results. This provides a basic but robust tool for exploring policy options.
      - **Phase 2: Advanced Optimization:** Integrate a general-purpose optimization library (e.g., Optuna) to intelligently and efficiently search the parameter space for optimal policies, building on the foundation from Phase 1.

10. **Historical Analysis Enhancements** *(In Progress)*
    - *Description:* Improve the model's capability to conduct robust historical analysis by incorporating economic and demographic changes over time.
    - *Tasks:*
      - **Inflation and Wage Adjustment:** Introduce a mechanism to adjust population incomes and monetary values to a common year's terms, enabling meaningful "real terms" comparisons of policy impacts across different eras.
      - **Demographic Evolution:** Develop a module to simulate changes in the population's structure over time (e.g., age distribution, family size), allowing for more realistic long-term analysis.
      - **Historical Reporting Framework:** Create dedicated reporting functions to generate standard outputs for historical comparisons, such as plots of effective tax rates or benefit entitlements by decile over time.
    - *Priority:* **Medium**
    - *Status:* **In Progress**. Foundational files exist.