# Feature Matrix

This document compares the features of the NZ-Microsim library with the original SAS models it is based on, as well as two other popular open-source microsimulation platforms: PolicyEngine and OpenFisca.

| Feature | NZ-Microsim (This Repo) | Original SAS Models | PolicyEngine | OpenFisca |
| --- | --- | --- | --- | --- |
| **Core Focus** | New Zealand tax and transfer system | New Zealand tax and transfer system | Multi-country tax and benefit systems | Generic microsimulation framework ("Legislation as code") |
| **Technology** | Python | SAS | Python | Python |
| **Open Source** | Yes (MIT License) | No (Proprietary) | Yes (AGPL-3.0) | Yes (AGPL-3.0) |
| **Core Engine** | Custom-built | Custom-built | PolicyEngine Core (fork of OpenFisca-Core) | OpenFisca-Core |
| **Modularity** | Modular design with pluggable components | Macro-based (`famsim`) | Highly modular (core engine + country packages) | Highly modular (core engine + country packages) |
| **Country Coverage** | New Zealand only | New Zealand only | US, UK, Canada | France, Spain, Senegal, and others |
| **Web Interface** | No | No | Yes (React-based web app) | Yes (via country packages) |
| **API** | No | No | Yes (REST API) | Yes (REST API) |
| **Parameterisation** | JSON files per tax year | Hardcoded in macros, with some input parameters | YAML files | YAML files |
| **Key Features** | - Income Tax<br>- Working for Families (WFF)<br>- FamilyBoost<br>- IETC<br>- RWT<br>- Superannuation<br>- Reporting & Sensitivity Analysis | - Income Tax<br>- Working for Families (WFF) | - Detailed tax and benefit calculations for each country<br>- Microdata generation<br>- Extensible with new policies | - Core calculus engine<br>- Domain-specific language for policy rules<br>- Handles complex dependencies between variables |
| **Extensibility** | Designed to be extensible | Limited | Designed to be extensible through new country packages or policies | Designed to be extensible through new country packages or policies |
| **Tax Year Coverage** | 2005-2025 | Not specified | Varies by country | Varies by country |
| **Community** | Small, focused on this project | Internal to Inland Revenue | Active community | Active community |
