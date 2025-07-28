# NZ Microsimulation Model

This project is a Python-based microsimulation model for the New Zealand tax and transfer system. It is a translation of the SAS-based models provided by Inland Revenue.

## Security

If you discover a security vulnerability, please report it responsibly. See our [docs/SECURITY.md](docs/SECURITY.md) for details.

## Contributing

We welcome contributions to this project. Please see our [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for detailed guidelines.

## License

This project is licensed under the MIT License - see the [docs/LICENSE](docs/LICENSE) file for details.

## Cite Us

If you use this software in your research, please cite it as per the guidelines in [docs/CITATION.cff](docs/CITATION.cff).

## Project Structure

This project is organized into the following main directories and files:

*   `src/`: Contains the core Python source code for the microsimulation model. See [src/README.md](src/README.md) for more details on the contents of this directory.
*   `sas_models/`: Stores the original SAS model files that this project translates and replicates. See [sas_models/README.md](sas_models/README.md) for more details on the contents of this directory.
*   `docs/`: Contains project documentation, including the economic analysis paper and model metadata. See [docs/README.md](docs/README.md) for more details on the contents of this directory.
*   `pyproject.toml`: Manages project dependencies, build configurations, and tool settings (e.g., `pytest`, `ruff`).
*   `Makefile`: Provides automated commands for common development tasks like testing, linting, and formatting.
*   `LICENSE`: Specifies the project's licensing (MIT License).
*   `CONTRIBUTING.md`: Guidelines for contributing to the project.
*   `CITATION.cff`: Information on how to cite this software in research.
*   `SECURITY.md`: Details on how to report security vulnerabilities.
*   `CHANGELOG.md`: Documents all notable changes to the project.
*   `examples/`: Contains example scripts demonstrating how to use the model.
*   `tests/`: Contains unit tests for the project. See [tests/README.md](tests/README.md) for more details on the contents of this directory.
*   `.github/`: Contains GitHub-specific configuration files. See [.github/README.md](.github/README.md) for more details on the contents of this directory.

## Project Goals

The primary goal of this project is to create a transparent, accessible, and extensible microsimulation model for New Zealand. This includes:

*   **Replicating Existing Functionality:** The initial focus is on replicating the functionality of the existing SAS models for income tax and Working for Families (WFF). The original SAS model files are located in the `sas_models/` directory.
*   **Project Structure:** Python source code is organized in the `src/` directory.
*   **Parameterization:** Where the original models use microdata, this project will use appropriate parameters and distributions to ensure the model is self-contained and does not require access to sensitive data.
*   **Dependency Management:** Project dependencies are managed using `pyproject.toml`.
*   **Testing and Documentation:** The project will include a comprehensive test suite to ensure the accuracy of the model and will be well-documented to facilitate understanding and use. Documentation files are located in the `docs/` directory.
*   **Economic Analysis:** The project includes an economic analysis of the model and its outputs, presented in the style of an economics paper. The draft paper is available in [docs/nz_microsim_paper.md](docs/nz_microsim_paper.md) and is a work in progress.
*   **Value of Information:** Sensitivity analysis utilities include a function to compute the Expected Value of Perfect Information (EVPI) from probabilistic results.

### Feature Status

| Feature | Status |
| --- | --- |
| Income Tax calculations | Implemented |
| Working for Families | Implemented |
| FamilyBoost credit | Implemented |
| Reporting utilities | Implemented |
| Sensitivity analysis tools | Implemented |
| Paid Parental Leave module | Optional |
| Child Support module | Optional |
| Sensitivity analysis tools | In progress |

## Changelog

See the [CHANGELOG.md](CHANGELOG.md) for a history of changes.

## Parameterization

The microsimulation model is designed to be flexible and easily adaptable to changes in tax policy. All key policy parameters, such as tax brackets, credit amounts, and abatement thresholds, can be stored in JSON files.

This allows you to run the model with different sets of policy rules, for example, for different years or for different policy scenarios.

### Loading Parameters

To load parameters for a specific tax year, use the `load_parameters` function from `src/microsim.py`, providing the year in "YYYY-YYYY" format:

```python
from src.microsim import load_parameters

# Load parameters for a specific year
params = load_parameters("2024-2025")

# Access specific parameters
tax_brackets = params["tax_brackets"]
ietc_params = params["ietc"]
```

### Example Usage

The `examples/basic_usage.py` script demonstrates how to use this system to calculate tax for different years by loading different parameter files.

The project currently includes parameter files for the following tax years, located in the `src/` directory:
* `parameters_2016-2017.json`
* `parameters_2017-2018.json`
* `parameters_2018-2019.json`
* `parameters_2019-2020.json`
* `parameters_2020-2021.json`
* `parameters_2021-2022.json`
* `parameters_2022-2023.json`
* `parameters_2024-2025.json`

### Budget Impact Analysis

To compare the fiscal outcomes of two scenarios, use
`calculate_budget_impact` from `src.budget_analysis`:

```python
import pandas as pd
from src.budget_analysis import calculate_budget_impact

baseline = pd.DataFrame(
    {
        "tax_liability": [100, 200],
        "jss_entitlement": [10, 20],
    }
)
reform = pd.DataFrame(
    {
        "tax_liability": [120, 230],
        "jss_entitlement": [15, 25],
    }
)

impact = calculate_budget_impact(baseline, reform)
print(impact)
```

This returns a table summarizing revenue, spending and the net fiscal impact for
each scenario and their difference.

### Inequality Metrics

The reporting utilities include helper functions for common inequality measures.
You can generate Lorenz curve data or compute the Atkinson and Theil indices:

```python
import pandas as pd
from src.reporting import lorenz_curve, atkinson_index, theil_index

incomes = pd.Series([0, 10, 20, 30, 40])

lorenz = lorenz_curve(incomes)
a_index = atkinson_index(incomes)
t_index = theil_index(incomes)
```

### Optional Modules

The model includes simple components for Paid Parental Leave (PPL) and child
support. These modules are off by default. To activate them, set
`ppl.enabled` or `child_support.enabled` to `true` in the parameter JSON file.
PPL requires `weekly_rate` and `max_weeks` values, while child support uses a
`support_rate` applied to the liable parent's income.

### Policy Comparison

To compare tax policies across different years, you can provide multiple parameter files to the `run-simulation` and `generate-reports` commands. This will run the simulation and generate comparative reports for each specified year.

For example, to compare the 2016-2017 and 2024-2025 tax policies:

```bash
make run-simulation PARAM_FILES="src/parameters_2016-2017.json src/parameters.json"
make generate-reports PARAM_FILES="src/parameters_2016-2017.json src/parameters.json"
```

## Usage

### Installation

To install the core project dependencies, run:
```bash
make install
```

If you're developing the project itself, you can install it in editable mode:

```bash
pip install -e .
```

The main Python packages used by the model are:

* `pandas`
* `numpy`
* `pydantic`
* `matplotlib`
* `seaborn`
* `joblib`
* `scipy`

### Running Examples

To see a basic example of how to use the microsimulation model, execute:

```bash
make run-example
```

## Roadmap

The following is a high-level roadmap for the project:

1.  **Achieve Parity with SAS Models:** The immediate priority is to achieve functional parity with the existing SAS models. This includes replicating the income tax and WFF calculations and ensuring the outputs are consistent with the original models.
2.  **Develop Additional Functionality:** Once parity is achieved, the project will explore adding additional functionality, such as:
    *   **Behavioral Responses:** Incorporating behavioral responses to policy changes, such as changes in labor supply or savings behavior.
    *   **Dynamic Simulation:** Extending the model to allow for dynamic simulation over time, including demographic and economic changes.
    *   **Integration with Other Models:** Exploring the potential for integrating the model with other social policy models in New Zealand.
3.  **Ongoing Maintenance and Improvement:** The project will be an ongoing effort, with continuous improvement of the model, documentation, and analysis.

## Development

This project uses a `Makefile` to automate common development tasks. You can find the available commands in the `Makefile` itself.

### Installing Development Dependencies

To install all development dependencies (including `pytest`, `ruff`, `pre-commit`, and `tabulate`) along with the project itself,
run:

```bash
make install-dev-deps
```

`tabulate` is required so that `DataFrame.to_markdown()` works correctly during tests.

### Running Tests
Before running the tests, ensure the development dependencies are installed.
Run `make install-dev-deps` — or `pip install -e .` followed by
`pip install -r requirements-dev.txt` — before executing `pytest`.

To run the unit tests for the project, execute:
```bash
make test
```

This will run all tests in `test_microsim.py` and `test_wff_microsim.py`.

### Linting and Formatting

This project uses [Ruff](https://beta.ruff.rs/docs/) for linting and formatting. To check for linting issues, run:

```bash
make lint
```

To automatically format the code, run:

```bash
make format
```

### Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) to ensure code quality before commits. After installing development dependencies, set up the pre-commit hooks by running:

```bash
pre-commit install
```

Once installed, the hooks will automatically run `ruff` checks and formatting on your staged files before each commit.

### Cleaning the Project

To remove build artifacts, cache directories, and Python bytecode files, run:

```bash
make clean
```
