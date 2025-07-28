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

## Modernization Roadmap

The following roadmap outlines the key steps to modernize the repository, improve development practices, and automate workflows.

1.  **Establish Robust Development Practices:**
    *   **Branching Strategy:** Implement a clear branching strategy (`main` for stable releases, feature branches for development) to ensure a clean and maintainable codebase. (Completed 2025-07-03)
    *   **Development Log:** Create a `development_log.md` to provide a transparent and consistent record of all development activities. (Completed 2025-07-03)
    *   **Contribution Guidelines:** Update `CONTRIBUTING.md` to reflect the new branching strategy and development workflow. (Completed 2025-07-03)

2.  **Automate Workflows with GitHub Actions:**
    *   **Continuous Integration (CI):** Create a CI pipeline (`.github/workflows/ci.yml`) that automatically runs on every push and pull request to:
        *   Install dependencies.
        *   Run the linter (`ruff`).
        *   Run the test suite (`pytest`).
    *   **Automated Release Notes:** Implement a process to automatically generate release notes from the `development_log.md` or commit messages.
    *   **Scheduled Tasks:** Explore opportunities for scheduled tasks, such as nightly builds or data updates.

3.  **Enhance Project Structure and Tooling:**
    *   **Dependency Management:** Review and update the dependency management process to ensure consistency and reliability.
    *   **Code Coverage:** Integrate a code coverage tool (e.g., `coverage.py`) into the CI pipeline to monitor test coverage.
    *   **Containerization:** Investigate the use of Docker to create a consistent and reproducible development environment.

4.  **Improve Documentation and Reporting:**
    *   **Automated Documentation:** Explore tools like Sphinx to automatically generate documentation from docstrings.
    *   **Interactive Reports:** Enhance the reporting framework to generate interactive data visualizations (e.g., using `plotly`).
    *   **API Documentation:** Create clear and comprehensive documentation for the model's API.

## Future Roadmap: AI Integration and Foundational Improvements

This roadmap prioritizes foundational robustness and usability before integrating advanced AI-driven features. The goal is to ensure the core system is accurate, reliable, and maintainable.

### Phase 1: Foundational Robustness (Core Model Integrity)

This phase is critical to ensure the quality and accuracy of the model's outputs, which is a prerequisite for any meaningful analysis or AI integration.

*   **Robust Data Validation & Cleaning:**
    *   **Why:** Ensures the integrity of input data. The principle of "garbage in, garbage out" means the model's outputs are only as reliable as its inputs. This is the bedrock for trustworthy results.
    *   **Effort:** Medium
    *   **Priority:** High
*   **Comprehensive Model Validation & Calibration:**
    *   **Why:** Guarantees the core tax rule logic is correct by testing against known outcomes and official statistics. This builds confidence in the model's predictive power.
    *   **Effort:** High
    *   **Priority:** High
*   **Enhanced Logging and Documentation:**
    *   **Why:** Improves transparency and makes debugging significantly easier for developers. Clear documentation lowers the barrier to entry for new contributors.
    *   **Effort:** Low
    *   **Priority:** High

### Phase 2: Usability and Performance

This phase focuses on making the model faster and easier to use for both developers and analysts.

*   **Performance Optimization:**
    *   **Why:** Faster execution allows for more complex simulations and quicker iteration during development and analysis.
    *   **Effort:** Medium
    *   **Priority:** Medium
*   **Scenario Management & Comparison Tools:**
    *   **Why:** This is a core function of a microsimulation model. It enables structured analysis of different policy scenarios and provides clear, comparable results.
    *   **Effort:** Medium
    *   **Priority:** Medium
*   **Basic User Interface (CLI):**
    *   **Why:** A simple Command-Line Interface (CLI) would make the model more accessible for running standard scenarios without needing to write Python code.
    *   **Effort:** Low
    *   **Priority:** Medium

### Phase 3: AI Integration (Proof of Concept)

With a robust foundation in place, this phase explores the feasibility of the AI reporting goal on a small scale.

*   **Develop AI Reporting Proof of Concept (PoC):**
    *   **Why:** To test the proposed AI architecture (local embedding and generative models) on a limited set of outputs. This will validate the approach and identify potential challenges early.
    *   **Effort:** Medium
    *   **Priority:** Low
*   **Structured Output for AI Consumption:**
    *   **Why:** Ensures that model outputs (tables, figures) are in a consistent, machine-readable format (e.g., JSON, CSV) that the AI pipeline can easily ingest.
    *   **Effort:** Low
    *   **Priority:** Low

### Phase 4: Full AI Integration and Advanced Features

This phase builds on the successful PoC to deliver the full AI-driven reporting vision.

*   **Full-Scale AI Report Generation:**
    *   **Why:** Implements the end-to-end AI pipeline, allowing the LLM to interpret a wide range of model outputs and generate detailed, context-aware text reports. This is the primary AI integration goal.
    *   **Effort:** High
    *   **Priority:** Low

## Upcoming Tasks

1. **Complete Sensitivity Analysis Tools**
   - *Milestone:* Finalize parameter sweep utilities and integrate with scenario management.
   - *Priority:* **High**

2. **Implement Value-of-Information Analysis**
   - *Milestone:* Add module for assessing the benefit of additional data sources or improved data quality.
   - *Priority:* **Medium**

3. **Budget Impact Modules**
   - *Milestone:* Build routines to aggregate fiscal costs and savings across scenarios.
   - *Priority:* **High**

4. **Expanded Equity Metrics**
   - *Milestone:* Introduce additional indicators of distributional effects (e.g., progressivity indexes).
   - *Priority:* **Medium**

*   **Advanced UI/Dashboard:**
    *   **Why:** A simple web-based UI could be developed to allow users to select scenarios, view results, and trigger AI-generated reports, making the tool accessible to non-technical users.
    *   **Effort:** High
    *   **Priority:** Low

## Progress Log

*   **2025-07-03:**
    *   Established a new branching strategy and updated `CONTRIBUTING.md`.
    *   Created `docs/development_log.md` to track changes.
    *   Updated the project roadmap to focus on modernization and automation.
*   **2025-07-02:**
    *   Parameterized the microsimulation model to allow for easy updates and comparisons between different tax years.
    *   Added historical tax rules for the years 2016-2021.
    *   Updated the model with the 2024-2025 composite tax rates, IETC, and IWTC changes.
    *   Added a new function for the FamilyBoost tax credit.
    *   Updated tests to use the new parameter system and verify the new rules.
    *   Updated examples/basic_usage.py to demonstrate the new system.
    *   Updated README.md to document the parameterization feature.
