| Feature                 | nztaxmicrosim                                       | OpenFisca                                            | PolicyEngine                                         |
| ----------------------- | --------------------------------------------------- | ---------------------------------------------------- | ---------------------------------------------------- |
| **Core Technology**     | Python (Pandas, Pydantic)                           | Python (Core framework)                              | Python (built on OpenFisca)                          |
| **Primary Focus**       | New Zealand tax and transfer system                 | General-purpose microsimulation framework            | Policy analysis for specific countries (UK, US)      |
| **Country Coverage**    | New Zealand only                                    | Multi-country (France, Spain, etc.)                  | UK and US                                            |
| **Rule Definition**     | JSON files for parameters, Python for logic         | Python-based Domain Specific Language (DSL)          | YAML for policy rules                                |
| **Extensibility**       | Modular pipeline, but self-contained                | Highly extensible framework for adding new countries/rules | Highly extensible, inherits from OpenFisca           |
| **User Interface**      | None (command-line/library)                         | None (provides API for UIs)                          | Web-based graphical user interface                   |
| **API**                 | Python library interface                            | REST API                                             | REST API                                             |
| **Data Input**          | Python scripts, CSV files                           | JSON via API                                         | Web UI, JSON via API                                 |
| **Community**           | Single project                                      | Open-source community with multiple contributors     | Open-source community with multiple contributors     |
| **Dynamic Simulation**  | Experimental support                                | Not a core feature                                   | Not a core feature                                   |
| **Sensitivity Analysis**| Built-in (including EVPI)                           | Not a core feature                                   | Core feature with web UI integration                 |
