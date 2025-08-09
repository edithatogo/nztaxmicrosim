import os
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def calculate_lorenz_curve(income_series: pd.Series) -> pd.DataFrame:
    """Calculate points for a Lorenz curve.

    The Lorenz curve is a graphical representation of the distribution of
    income or wealth. This function calculates the cumulative shares of
    population and income, which can be used to plot the curve.

    Args:
        income_series: A pandas Series of income values.

    Returns:
        A DataFrame with 'population_share' and 'income_share' columns.
    """
    if income_series.empty:
        return pd.DataFrame({"population_share": [0.0], "income_share": [0.0]})

    sorted_income = income_series.clip(lower=0).sort_values().to_numpy()
    cum_income = np.cumsum(sorted_income)
    total_income = cum_income[-1]
    population_share = np.arange(1, len(sorted_income) + 1) / len(sorted_income)
    income_share = cum_income / total_income if total_income != 0 else cum_income

    # Prepend origin (0,0)
    population_share = np.insert(population_share, 0, 0.0)
    income_share = np.insert(income_share, 0, 0.0)
    return pd.DataFrame({"population_share": population_share, "income_share": income_share})


def calculate_atkinson_index(income_series: pd.Series, epsilon: float = 0.5) -> float:
    """Calculate the Atkinson index for a given income series.

    The Atkinson index is a measure of income inequality. It is defined as
    1 minus the ratio of the equally distributed equivalent income to the
    mean income.

    Args:
        income_series: A pandas Series of income values.
        epsilon: The inequality aversion parameter. A higher value means
            more weight is given to inequalities at the lower end of the
            distribution.

    Returns:
        The Atkinson index.
    """
    values = income_series[income_series > 0].to_numpy()
    if values.size == 0:
        return 0.0

    mean_income = values.mean()
    if epsilon == 1:
        geo_mean = np.exp(np.log(values).mean())
        return 1 - geo_mean / mean_income
    else:
        exp_val = (values ** (1 - epsilon)).mean() ** (1 / (1 - epsilon))
        return 1 - exp_val / mean_income


def calculate_theil_index(income_series: pd.Series) -> float:
    """Calculate the Theil T index for a given income series.

    The Theil index is a measure of economic inequality. It is a special
    case of the generalized entropy index.

    Args:
        income_series: A pandas Series of income values.

    Returns:
        The Theil T index.
    """
    values = income_series[income_series > 0].to_numpy()
    if values.size == 0:
        return 0.0

    mean_income = values.mean()
    ratios = values / mean_income
    return float(np.mean(ratios * np.log(ratios)))


def calculate_reynolds_smolensky_index(pre_tax_income: pd.Series, post_tax_income: pd.Series) -> float:
    """Calculate the Reynolds-Smolensky index of tax progressivity.

    The Reynolds-Smolensky index is a measure of the vertical equity of a
    tax system. It is defined as the difference between the Gini
    coefficient of pre-tax income and the Gini coefficient of post-tax
    income.

    Args:
        pre_tax_income: A pandas Series of pre-tax income values.
        post_tax_income: A pandas Series of post-tax income values.

    Returns:
        The Reynolds-Smolensky index.
    """
    stats_helper = DistributionalStatisticsTable()
    gini_pre_tax = stats_helper._calculate_gini_coefficient(pre_tax_income)
    gini_post_tax = stats_helper._calculate_gini_coefficient(post_tax_income)
    return gini_pre_tax - gini_post_tax


# Define a base class for report components to ensure modularity and a common interface
class ReportComponent:
    """A base class for all components that can be included in a report.

    This class defines the common interface for all report components,
    ensuring that they can be generated and converted to Markdown in a
    consistent way.
    """

    def __init__(self, title: str, description: str):
        self.title = title
        self.description = description

    def generate(self, data: pd.DataFrame, params: Dict[str, Any]) -> Any:
        """Generate the content for the report component.

        This method should be overridden by subclasses to implement the
        specific logic for generating the component's content (e.g., a
        DataFrame, a plot, or a string).

        Args:
            data: The input data for generating the component.
            params: A dictionary of parameters specific to the component.

        Returns:
            The generated report component content.
        """
        raise NotImplementedError("Generate method must be implemented by subclasses.")

    def to_markdown(self, content: Any) -> str:
        """Convert the generated component content to a Markdown string.

        This method can be overridden by subclasses to provide custom
        Markdown formatting for the component's content.

        Args:
            content: The content generated by the `generate` method.

        Returns:
            A Markdown-formatted string representing the component.
        """
        return f"""## {self.title}

{self.description}

{content}
"""


# --- Section Components ---


class ExecutiveSummary(ReportComponent):
    """A report component for generating an executive summary."""
    def __init__(self):
        super().__init__(
            title="Executive Summary", description="Concise overview of key objectives, assumptions, and findings."
        )

    def generate(self, data: pd.DataFrame, params: Dict[str, Any]) -> str:
        """Generate a summary of the key findings from the simulation.

        This method should be updated to summarize the main results from the
        simulation data.

        Args:
            data: The simulation data.
            params: The parameters for the report.

        Returns:
            A string containing the executive summary.
        """
        # This would typically involve summarizing key metrics from 'data'
        # For now, a placeholder
        summary_text = (
            "This report presents the findings from the microsimulation model, "
            "highlighting the fiscal and distributional impacts of the simulated policies. "
            "Key findings indicate [summarize main results here]."
        )
        return summary_text


# --- Table Components ---


class FiscalImpactTable(ReportComponent):
    """A report component for summarizing the fiscal impact of a policy."""
    def __init__(self):
        super().__init__(
            title="Fiscal Impact Summary", description="Simulation of total revenue and benefit spending by category."
        )

    def _calculate_total_tax_revenue(self, df: pd.DataFrame) -> float:
        """Calculate the total tax revenue from the 'tax_liability' column."""
        if "tax_liability" not in df.columns:
            return 0.0
        return df["tax_liability"].sum()

    def _calculate_total_welfare_transfers(self, df: pd.DataFrame) -> float:
        """Calculate the total welfare transfers from various entitlement columns."""
        total_welfare = 0.0
        for col in [
            "jss_entitlement",
            "sps_entitlement",
            "slp_entitlement",
            "accommodation_supplement_entitlement",
            "wep_entitlement",
            "bstc_entitlement",
            "ftc_entitlement",
            "iwtc_entitlement",
            "mftc_entitlement",
        ]:
            total_welfare += df.get(col, pd.Series([0])).sum()
        return total_welfare

    def _calculate_net_fiscal_impact(self, tax_revenue: float, welfare_transfers: float) -> float:
        """Calculate the net fiscal impact."""
        return tax_revenue - welfare_transfers

    def generate(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Generate a table summarizing the fiscal impact of the policy.

        The table includes the total tax revenue, total welfare transfers, and
        the net fiscal impact.

        Args:
            data: The simulation data.
            params: The parameters for the report.

        Returns:
            A DataFrame containing the fiscal impact summary.
        """
        total_tax_revenue = self._calculate_total_tax_revenue(data)
        total_welfare_transfers = self._calculate_total_welfare_transfers(data)
        net_fiscal_impact = self._calculate_net_fiscal_impact(total_tax_revenue, total_welfare_transfers)

        fiscal_data = {
            "Metric": ["Total Tax Revenue", "Total Welfare Transfers", "Net Fiscal Impact"],
            "Value": [total_tax_revenue, total_welfare_transfers, net_fiscal_impact],
        }
        return pd.DataFrame(fiscal_data)

    def to_markdown(self, content: pd.DataFrame) -> str:
        return f"""## {self.title}

{self.description}

{content.to_markdown(index=False)}
"""


class DistributionalStatisticsTable(ReportComponent):
    """A report component for summarizing the distributional statistics of income."""
    def __init__(self):
        super().__init__(
            title="Distributional Statistics",
            description="Summary of mean/median incomes, poverty rates, Gini, before/after reform.",
        )

    def _calculate_disposable_income(self, df: pd.DataFrame) -> pd.Series:
        """Calculate disposable income before housing costs."""
        disposable_income = df["familyinc"]
        for col in [
            "jss_entitlement",
            "sps_entitlement",
            "slp_entitlement",
            "accommodation_supplement_entitlement",
        ]:
            disposable_income += df[col]
        for col in ["FTCcalc", "IWTCcalc", "BSTCcalc", "MFTCcalc"]:
            disposable_income += df.get(col, 0)
        if "tax_liability" in df.columns:
            disposable_income -= df["tax_liability"]
        return disposable_income

    def _calculate_disposable_income_ahc(self, df: pd.DataFrame) -> pd.Series:
        """Calculate disposable income after housing costs."""
        disposable_income = self._calculate_disposable_income(df)
        if "housing_costs" in df.columns:
            return disposable_income - df["housing_costs"]
        return disposable_income

    def _calculate_poverty_rate(self, income_series: pd.Series, poverty_line: float) -> float:
        """Calculate the poverty rate for a given income series and poverty line."""
        if income_series.empty:
            return 0.0
        return (income_series < poverty_line).sum() / len(income_series) * 100

    def _calculate_gini_coefficient(self, income_series: pd.Series) -> float:
        """Calculate the Gini coefficient for a given income series."""
        if income_series.empty or len(income_series) == 1:
            return 0.0
        sorted_income = income_series.sort_values().values
        n = len(sorted_income)
        numerator = np.sum((2 * np.arange(1, n + 1) - n - 1) * sorted_income)
        denominator = n * sorted_income.sum()
        return numerator / denominator if denominator != 0 else 0.0

    def generate(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Generate a table of distributional statistics.

        The table includes mean and median disposable income, the poverty line,
        the poverty rate, and the Gini coefficient. It also includes these
        statistics for after-housing-cost (AHC) income if available.

        Args:
            data: The simulation data.
            params: The parameters for the report, including the relative
                poverty line.

        Returns:
            A DataFrame containing the distributional statistics.
        """
        disposable_income = self._calculate_disposable_income(data)
        disposable_income_ahc = self._calculate_disposable_income_ahc(data)

        poverty_line_relative = params.get("poverty_line_relative", 0.5)

        median_income = disposable_income.median()
        poverty_line = median_income * poverty_line_relative

        poverty_rate = self._calculate_poverty_rate(disposable_income, poverty_line)
        gini_coefficient = self._calculate_gini_coefficient(disposable_income)

        stats_data = {
            "Metric": [
                "Mean Disposable Income",
                "Median Disposable Income",
                "Poverty Line (50% Median)",
                "Poverty Rate (%)",
                "Gini Coefficient",
            ],
            "Value": [disposable_income.mean(), median_income, poverty_line, poverty_rate, gini_coefficient],
        }

        if not disposable_income_ahc.empty:
            median_income_ahc = disposable_income_ahc.median()
            poverty_line_ahc = median_income_ahc * poverty_line_relative
            poverty_rate_ahc = self._calculate_poverty_rate(disposable_income_ahc, poverty_line_ahc)
            gini_coefficient_ahc = self._calculate_gini_coefficient(disposable_income_ahc)

            stats_data["Metric"].extend(
                [
                    "Mean Disposable Income AHC",
                    "Median Disposable Income AHC",
                    "Poverty Line AHC (50% Median)",
                    "Poverty Rate AHC (%)",
                    "Gini Coefficient AHC",
                ]
            )
            stats_data["Value"].extend(
                [
                    disposable_income_ahc.mean(),
                    median_income_ahc,
                    poverty_line_ahc,
                    poverty_rate_ahc,
                    gini_coefficient_ahc,
                ]
            )

        return pd.DataFrame(stats_data)

    def to_markdown(self, content: pd.DataFrame) -> str:
        if isinstance(content, str):
            return content
        return f"""## {self.title}

{self.description}

{content.to_markdown(index=False)}
"""


# --- Figure Components ---


class EquityMetricsTable(ReportComponent):
    """A report component for summarizing key equity metrics."""
    def __init__(self):
        super().__init__(
            title="Equity Metrics",
            description="Summary of key equity metrics.",
        )

    def _calculate_market_income(self, df: pd.DataFrame) -> pd.Series:
        """Calculate market income from various income columns."""
        market_income = (
            df.get("employment_income", 0)
            + df.get("self_employment_income", 0)
            + df.get("investment_income", 0)
            + df.get("rental_property_income", 0)
            + df.get("private_pensions_annuities", 0)
        )
        return market_income

    def generate(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Generate a table of equity metrics.

        The table includes the Gini coefficient, Atkinson index, Theil index,
        and Reynolds-Smolensky index.

        Args:
            data: The simulation data.
            params: The parameters for the report.

        Returns:
            A DataFrame containing the equity metrics.
        """
        market_income = self._calculate_market_income(data)
        disposable_income = DistributionalStatisticsTable()._calculate_disposable_income(data)

        gini = DistributionalStatisticsTable()._calculate_gini_coefficient(disposable_income)
        atkinson = calculate_atkinson_index(disposable_income)
        theil = calculate_theil_index(disposable_income)
        reynolds_smolensky = calculate_reynolds_smolensky_index(market_income, disposable_income)

        equity_data = {
            "Metric": [
                "Gini Coefficient (Disposable Income)",
                "Atkinson Index (Disposable Income, e=0.5)",
                "Theil Index (Disposable Income)",
                "Reynolds-Smolensky Index",
            ],
            "Value": [gini, atkinson, theil, reynolds_smolensky],
        }
        return pd.DataFrame(equity_data)

    def to_markdown(self, content: pd.DataFrame) -> str:
        return f"""## {self.title}

{self.description}

{content.to_markdown(index=False)}
"""


class IncomeDecileImpactChart(ReportComponent):
    """A report component for visualizing the impact on different income deciles."""
    def __init__(self):
        super().__init__(
            title="Tax/Benefit Impact by Income Decile", description="Bar or line chart of net effect on each decile."
        )

    def generate(self, data: pd.DataFrame, params: Dict[str, Any]) -> plt.Figure:
        """Generate a bar chart of average disposable income per income decile.

        Args:
            data: The simulation data, which must contain a
                `disposable_income` column.
            params: The parameters for the report.

        Returns:
            A matplotlib Figure object containing the chart.
        """
        # Requires 'disposable_income' and a way to calculate deciles
        if "disposable_income" not in data.columns:
            raise ValueError("DataFrame must contain 'disposable_income' column.")

        # Calculate deciles based on disposable income
        data["income_decile"] = (
            pd.qcut(data["disposable_income"], 10, labels=False, duplicates="drop") + 1
        )  # +1 to make deciles 1-10

        # Calculate average disposable income per decile
        decile_impact = data.groupby("income_decile")["disposable_income"].mean().reset_index()

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x="income_decile", y="disposable_income", data=decile_impact, ax=ax)
        ax.set_title(self.title)
        ax.set_xlabel("Income Decile")
        ax.set_ylabel("Average Disposable Income")
        plt.close(fig)  # Close the figure to prevent it from being displayed immediately
        return fig

    def to_markdown(self, content: Any) -> str:
        if isinstance(content, str) and content.startswith("Error:"):
            return f"""## {self.title}

{self.description}

{content}
"""
        # Save the figure to a temporary file and embed its path in markdown
        # In a real scenario, you'd save to a designated reports directory
        filepath = f"reports/{self.title.replace(' ', '_').lower()}.png"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        content.savefig(filepath)
        return f"""## {self.title}

{self.description}

![{self.title}]({filepath})
"""


class PovertyRateChangesChart(ReportComponent):
    """A report component for visualizing changes in poverty rates."""
    def __init__(self):
        super().__init__(
            title="Poverty Rate Changes by Group",
            description="Chart of reform effect on poverty by category (e.g. age).",
        )

    def generate(self, data: pd.DataFrame, params: Dict[str, Any]) -> plt.Figure:
        """Generate a bar chart of poverty rates by age group.

        This is a placeholder implementation. A real implementation would
        compare baseline and reform scenarios.

        Args:
            data: The simulation data, which must contain `disposable_income`
                and `age` columns.
            params: The parameters for the report, including the relative
                poverty line.

        Returns:
            A matplotlib Figure object containing the chart.
        """
        # This is a placeholder. Real implementation would compare baseline vs. reform
        # and group by categories like 'age_group', 'household_type', etc.
        if "disposable_income" not in data.columns or "age" not in data.columns:
            raise ValueError("DataFrame must contain 'disposable_income' and 'age' columns.")

        poverty_line_relative = params.get("poverty_line_relative", 0.5)
        median_income = data["disposable_income"].median()
        poverty_line = median_income * poverty_line_relative

        # Example: Poverty rate by age group
        data["age_group"] = pd.cut(data["age"], bins=[0, 18, 65, 100], labels=["Child", "Adult", "Senior"])

        poverty_by_group = (
            data.groupby("age_group", observed=False)["disposable_income"]
            .apply(lambda x: (x < poverty_line).mean() * 100)
            .reset_index(name="poverty_rate")
        )

        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(x="age_group", y="poverty_rate", data=poverty_by_group, ax=ax)
        ax.set_title(self.title)
        ax.set_xlabel("Age Group")
        ax.set_ylabel("Poverty Rate (%)")
        plt.close(fig)
        return fig

    def to_markdown(self, content: plt.Figure) -> str:
        if isinstance(content, str) and content.startswith("Error:"):
            return f"""## {self.title}

{self.description}

{content}
"""
        filepath = f"reports/{self.title.replace(' ', '_').lower()}.png"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        content.savefig(filepath)
        return f"""## {self.title}

{self.description}

![{self.title}]({filepath})
"""


# --- Report Generation Orchestration ---


class ReportGenerator:
    """A class for orchestrating the generation of a multi-component report."""
    def __init__(self, components: List[ReportComponent]):
        self.components = components
        self.generated_content: Dict[str, Any] = {}

    def generate_report(self, data: pd.DataFrame, global_params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate all the components of the report.

        This method iterates through the list of components and calls their
        `generate` method, storing the results in a dictionary.

        Args:
            data: The simulation data.
            global_params: A dictionary of global parameters for the report.

        Returns:
            A dictionary containing the generated content for each component.
        """
        for component in self.components:
            try:
                # Pass global_params to each component's generate method
                self.generated_content[component.title] = component.generate(data.copy(), global_params)
            except Exception as e:
                print(f"Error generating {component.title}: {e}")
                self.generated_content[component.title] = f"Error: {e}"
        return self.generated_content

    def to_markdown_report(self) -> str:
        """Compile the generated components into a single Markdown report.

        This method iterates through the generated content and uses each
        component's `to_markdown` method to create a single string in
        Markdown format.

        Returns:
            A string containing the full Markdown report.
        """
        markdown_output = []
        for title, content in self.generated_content.items():
            # Find the component object to call its specific to_markdown method
            component = next((comp for comp in self.components if comp.title == title), None)
            if component:
                markdown_output.append(component.to_markdown(content))
            else:
                markdown_output.append(f"""## {title}
{content}
""")
        return "\n".join(markdown_output)


# Example Usage (for testing/demonstration)
if __name__ == "__main__":
    # Create dummy data for demonstration
    np.random.seed(42)
    num_people = 1000
    dummy_data = pd.DataFrame(
        {
            "employment_income": np.random.normal(50000, 15000, num_people),
            "self_employment_income": np.random.normal(5000, 2000, num_people),
            "investment_income": np.random.normal(1000, 500, num_people),
            "rental_property_income": np.random.normal(2000, 1000, num_people),
            "private_pensions_annuities": np.random.normal(3000, 1000, num_people),
            "tax_liability": np.random.normal(8000, 3000, num_people).clip(min=0),
            "jss_entitlement": np.random.normal(100, 50, num_people).clip(min=0),  # weekly
            "sps_entitlement": np.random.normal(50, 20, num_people).clip(min=0),  # weekly
            "slp_entitlement": np.random.normal(30, 10, num_people).clip(min=0),  # weekly
            "accommodation_supplement_entitlement": np.random.normal(20, 10, num_people).clip(min=0),  # weekly
            "FTCcalc": np.random.normal(1000, 300, num_people).clip(min=0),  # annual
            "IWTCcalc": np.random.normal(500, 200, num_people).clip(min=0),  # annual
            "BSTCcalc": np.random.normal(200, 100, num_people).clip(min=0),  # annual
            "MFTCcalc": np.random.normal(150, 50, num_people).clip(min=0),  # annual
            "housing_costs": np.random.normal(200, 50, num_people).clip(min=0),  # weekly
            "age": np.random.randint(0, 90, num_people),
        }
    )

    # Calculate disposable income and AHC for dummy data
    # These functions would ideally come from src/reporting.py or a shared utility
    def calculate_disposable_income_dummy(df: pd.DataFrame) -> pd.Series:
        disposable_income = (
            df["employment_income"]
            + df["self_employment_income"]
            + df["investment_income"]
            + df["rental_property_income"]
            + df["private_pensions_annuities"]
        )
        for col in ["jss_entitlement", "sps_entitlement", "slp_entitlement", "accommodation_supplement_entitlement"]:
            disposable_income += df[col] * 52
        for col in ["FTCcalc", "IWTCcalc", "BSTCcalc", "MFTCcalc"]:
            disposable_income += df[col]
        disposable_income -= df["tax_liability"]
        return disposable_income

    def calculate_disposable_income_ahc_dummy(df: pd.DataFrame) -> pd.Series:
        disposable_income = calculate_disposable_income_dummy(df)
        return disposable_income - (df["housing_costs"] * 52)

    dummy_data["disposable_income"] = calculate_disposable_income_dummy(dummy_data)
    dummy_data["disposable_income_ahc"] = calculate_disposable_income_ahc_dummy(dummy_data)

    # Instantiate report components
    components = [
        ExecutiveSummary(),
        FiscalImpactTable(),
        DistributionalStatisticsTable(),
        IncomeDecileImpactChart(),
        PovertyRateChangesChart(),
    ]

    # Create a ReportGenerator instance
    report_gen = ReportGenerator(components)

    # Define global parameters for the report
    global_report_params = {
        "poverty_line_relative": 0.6  # Example: 60% of median income for poverty line
    }

    # Generate the report
    generated_report_content = report_gen.generate_report(dummy_data, global_report_params)

    # Compile to Markdown
    full_markdown_report = report_gen.to_markdown_report()

    # Print the markdown report (or save to file)
    print(full_markdown_report)

    # To ensure matplotlib figures are saved, create a dummy reports directory if it doesn't exist
    import os

    if not os.path.exists("reports"):
        os.makedirs("reports")
    print("Dummy report components generated and saved to 'reports/' directory.")
