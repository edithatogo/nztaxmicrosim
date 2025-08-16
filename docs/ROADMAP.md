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

4. **Dynamic Behavioural Extensions** ✅
   - *Milestone:* Introduce modules that capture behavioural responses and longitudinal impacts of policy changes.
   - *Priority:* **Medium**
   - *Status:* **Done**. The core framework for EMTR calculation and labour supply response is complete.

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
  - *Status:* **Done** ✅
- **Q4 2025:** Release budget impact functionality alongside the first round of new equity metrics and value-of-information analysis.
  - *Status:* **Done** ✅

## Future Features

<<<<<<< HEAD
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

4. **Dynamic Behavioural Extensions** ✅
   - *Milestone:* Introduce modules that capture behavioural responses and longitudinal impacts of policy changes.
   - *Priority:* **Medium**
   - *Status:* **Done**. The core framework for EMTR calculation and labour supply response is complete.

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
  - *Status:* **Done** ✅
- **Q4 2025:** Release budget impact functionality alongside the first round of new equity metrics and value-of-information analysis.
  - *Status:* **Done** ✅

## Future Features

9. **Policy Optimisation Module** ✅
    - *Description:* Introduce a module to search for optimal policy parameters based on user-defined objectives (e.g., maximizing revenue while minimizing inequality).
    - *Priority:* **Low**
    - *Status:* **Done**
    - *Implementation Plan:*
      - **Phase 1: Simple Parameter Scanning:** Develop the core infrastructure to programmatically run the simulation with a grid of different input parameters and save the results. This provides a basic but robust tool for exploring policy options. ✅
      - **Phase 2: Advanced Optimization:** Integrate a general-purpose optimization library (e.g., Optuna) to intelligently and efficiently search the parameter space for optimal policies, building on the foundation from Phase 1. ✅

10. **Historical Analysis Enhancements** ✅
    - *Description:* Improve the model's capability to conduct robust historical analysis by incorporating economic and demographic changes over time.
    - *Tasks:*
      - **Inflation and Wage Adjustment:** Introduce a mechanism to adjust population incomes and monetary values to a common year's terms, enabling meaningful "real terms" comparisons of policy impacts across different eras. ✅
      - **Demographic Evolution:** Develop a module to simulate changes in the population's structure over time (e.g., age distribution, family size), allowing for more realistic long-term analysis. ✅
      - **Historical Reporting Framework:** Create dedicated reporting functions to generate standard outputs for historical comparisons, such as plots of effective tax rates or benefit entitlements by decile over time. ✅
    - *Priority:* **Medium**
    - *Status:* **Done**.

## Architectural Improvements

This section outlines potential future work focused on improving the core architecture, maintainability, and extensibility of the model.

11. **Configuration-Driven Pipelines** ✅
    - *Description:* Refactor the simulation execution logic to be driven by configuration files instead of hardcoded Python scripts. This would involve integrating a library like Kedro to define the sequence of rules and their parameters in YAML, making the model more flexible and easier to modify for non-developers.
    - *Priority:* **Medium**
    - *Status:* **Done**

12. **Parameter Database** ✅
    - *Description:* Migrate the historical policy parameters from individual JSON files to a structured database (e.g., SQLite). This would improve data integrity, make historical data easier to manage and query, and allow for robust validation of policy start and end dates at the data layer.
    - *Priority:* **Medium**
    - *Status:* **Done**

13. **Web API**
    - *Description:* Expose the simulation engine via a lightweight web API using a framework like FastAPI. This would make the model accessible to a wider range of tools and programming languages (R, Julia, etc.) without requiring language-specific wrappers.
    - *Priority:* **Low**
    - *Status:* **Not Started**

14. **Enhanced CI/CD**
    - *Description:* Improve the Continuous Integration/Continuous Deployment pipeline.
    - *Tasks:*
      - **Activate Dynamic Badges:** Integrate with services like Codecov and PyPI to make the README badges live.
      - **Automated Data Audit:** Add a CI job that automatically validates the historical accuracy of parameter files, preventing data errors from being merged.
      - **Performance Regression Testing:** Add a CI job that runs the profiler and fails if a pull request introduces a significant performance regression to core functions.
    - *Priority:* **Low**
    - *Status:* **Not Started**

=======
9. **Policy Optimisation Module** ✅
    - *Description:* Introduce a module to search for optimal policy parameters based on user-defined objectives (e.g., maximizing revenue while minimizing inequality).
    - *Priority:* **Low**
    - *Status:* **Done**
    - *Implementation Plan:*
      - **Phase 1: Simple Parameter Scanning:** Develop the core infrastructure to programmatically run the simulation with a grid of different input parameters and save the results. This provides a basic but robust tool for exploring policy options. ✅
      - **Phase 2: Advanced Optimization:** Integrate a general-purpose optimization library (e.g., Optuna) to intelligently and efficiently search the parameter space for optimal policies, building on the foundation from Phase 1. ✅
>>>>>>> origin/update-a-bunch-of-stuff-7

10. **Historical Analysis Enhancements** ✅
    - *Description:* Improve the model's capability to conduct robust historical analysis by incorporating economic and demographic changes over time.
    - *Tasks:*
      - **Inflation and Wage Adjustment:** Introduce a mechanism to adjust population incomes and monetary values to a common year's terms, enabling meaningful "real terms" comparisons of policy impacts across different eras. ✅
      - **Demographic Evolution:** Develop a module to simulate changes in the population's structure over time (e.g., age distribution, family size), allowing for more realistic long-term analysis. ✅
      - **Historical Reporting Framework:** Create dedicated reporting functions to generate standard outputs for historical comparisons, such as plots of effective tax rates or benefit entitlements by decile over time. ✅
    - *Priority:* **Medium**
    - *Status:* **Done**.

## Architectural Improvements
<<<<<<< HEAD
=======

This section outlines potential future work focused on improving the core architecture, maintainability, and extensibility of the model.

11. **Configuration-Driven Pipelines** ✅
    - *Description:* Refactor the simulation execution logic to be driven by configuration files instead of hardcoded Python scripts. This would involve integrating a library like Kedro to define the sequence of rules and their parameters in YAML, making the model more flexible and easier to modify for non-developers.
    - *Priority:* **Medium**
    - *Status:* **Done**

12. **Parameter Database** ✅
    - *Description:* Migrate the historical policy parameters from individual JSON files to a structured database (e.g., SQLite). This would improve data integrity, make historical data easier to manage and query, and allow for robust validation of policy start and end dates at the data layer.
    - *Priority:* **Medium**
    - *Status:* **Done**

13. **Web API**
    - *Description:* Expose the simulation engine via a lightweight web API using a framework like FastAPI. This would make the model accessible to a wider range of tools and programming languages (R, Julia, etc.) without requiring language-specific wrappers.
    - *Priority:* **Low**
    - *Status:* **Not Started**

14. **Enhanced CI/CD**
    - *Description:* Improve the Continuous Integration/Continuous Deployment pipeline.
    - *Tasks:*
      - **Activate Dynamic Badges:** Integrate with services like Codecov and PyPI to make the README badges live.
      - **Automated Data Audit:** Add a CI job that automatically validates the historical accuracy of parameter files, preventing data errors from being merged.
      - **Performance Regression Testing:** Add a CI job that runs the profiler and fails if a pull request introduces a significant performance regression to core functions.
    - *Priority:* **Low**
    - *Status:* **Not Started**
>>>>>>> origin/update-a-bunch-of-stuff-7

This section outlines potential future work focused on improving the core architecture, maintainability, and extensibility of the model.

11. **Configuration-Driven Pipelines**
    - *Description:* Refactor the simulation execution logic to be driven by configuration files instead of hardcoded Python scripts. This would involve integrating a library like Kedro to define the sequence of rules and their parameters in YAML, making the model more flexible and easier to modify for non-developers.
    - *Priority:* **Medium**
    - *Status:* **Done**

12. **Parameter Database**
    - *Description:* Migrate the historical policy parameters from individual JSON files to a structured database (e.g., SQLite). This would improve data integrity, make historical data easier to manage and query, and allow for robust validation of policy start and end dates at the data layer.
    - *Priority:* **Medium**
    - *Status:* **Done**

13. **Web API**
    - *Description:* Expose the simulation engine via a lightweight web API using a framework like FastAPI. This would make the model accessible to a wider range of tools and programming languages (R, Julia, etc.) without requiring language-specific wrappers.
    - *Priority:* **Low**
    - *Status:* **Not Started**

14. **Enhanced CI/CD**
    - *Description:* Improve the Continuous Integration/Continuous Deployment pipeline.
    - *Tasks:*
      - **Activate Dynamic Badges:** Integrate with services like Codecov and PyPI to make the README badges live.
      - **Automated Data Audit:** Add a CI job that automatically validates the historical accuracy of parameter files, preventing data errors from being merged.
      - **Performance Regression Testing:** Add a CI job that runs the profiler and fails if a pull request introduces a significant performance regression to core functions.
    - *Priority:* **Low**
    - *Status:* **Not Started**