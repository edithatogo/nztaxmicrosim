"""
Standardized report templates for policy analysis.
Builds on the existing reporting framework to provide researcher-friendly output.
"""

import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Template

from ..reporting import (
    calculate_gini_coefficient,
    calculate_poverty_rate,
    calculate_total_tax_revenue,
    calculate_total_welfare_transfers,
    calculate_disposable_income,
    calculate_budget_impact
)


class PolicyAnalysisReport:
    """
    Generates standardized policy analysis reports for researchers and policymakers.
    """
    
    def __init__(self, baseline_data: pd.DataFrame, scenario_data: pd.DataFrame, 
                 scenario_name: str, baseline_name: str = "Current Policy"):
        self.baseline_data = baseline_data
        self.scenario_data = scenario_data
        self.scenario_name = scenario_name
        self.baseline_name = baseline_name
        self.report_date = datetime.datetime.now()
        
    def generate_executive_summary(self) -> Dict[str, Union[str, float, int]]:
        """Generate key metrics for executive summary."""
        
        # Calculate key distributional metrics
        baseline_gini = calculate_gini_coefficient(self.baseline_data["disposable_income"])
        scenario_gini = calculate_gini_coefficient(self.scenario_data["disposable_income"])
        
        baseline_poverty = calculate_poverty_rate(self.baseline_data, threshold=0.6)
        scenario_poverty = calculate_poverty_rate(self.scenario_data, threshold=0.6)
        
        # Calculate fiscal impacts
        baseline_tax = calculate_total_tax_revenue(self.baseline_data)
        scenario_tax = calculate_total_tax_revenue(self.scenario_data)
        
        baseline_transfers = calculate_total_welfare_transfers(self.baseline_data)
        scenario_transfers = calculate_total_welfare_transfers(self.scenario_data)
        
        # Calculate winners and losers
        income_diff = self.scenario_data["disposable_income"] - self.baseline_data["disposable_income"]
        winners = len(income_diff[income_diff > 50])  # More than $50 better off
        losers = len(income_diff[income_diff < -50])   # More than $50 worse off
        unchanged = len(income_diff[(income_diff >= -50) & (income_diff <= 50)])
        
        return {
            "scenario_name": self.scenario_name,
            "baseline_name": self.baseline_name,
            "analysis_date": self.report_date.strftime("%B %d, %Y"),
            
            # Distributional impacts
            "gini_change": scenario_gini - baseline_gini,
            "poverty_change": scenario_poverty - baseline_poverty,
            "gini_pct_change": ((scenario_gini - baseline_gini) / baseline_gini) * 100,
            "poverty_pct_change": ((scenario_poverty - baseline_poverty) / baseline_poverty) * 100,
            
            # Fiscal impacts
            "tax_revenue_change": scenario_tax - baseline_tax,
            "transfer_change": scenario_transfers - baseline_transfers,
            "net_fiscal_impact": (scenario_tax - baseline_tax) - (scenario_transfers - baseline_transfers),
            
            # Population impacts
            "total_population": len(self.scenario_data),
            "winners": winners,
            "losers": losers,
            "unchanged": unchanged,
            "winners_pct": (winners / len(self.scenario_data)) * 100,
            "losers_pct": (losers / len(self.scenario_data)) * 100,
            
            # Income impacts
            "median_income_change": self.scenario_data["disposable_income"].median() - self.baseline_data["disposable_income"].median(),
            "mean_income_change": self.scenario_data["disposable_income"].mean() - self.baseline_data["disposable_income"].mean(),
        }
    
    def generate_decile_analysis(self) -> pd.DataFrame:
        """Analyze impact by income deciles."""
        
        # Create income deciles based on baseline
        baseline_deciles = pd.qcut(self.baseline_data["disposable_income"], 10, labels=False) + 1
        
        decile_analysis = []
        
        for decile in range(1, 11):
            decile_mask = baseline_deciles == decile
            
            baseline_subset = self.baseline_data[decile_mask]
            scenario_subset = self.scenario_data[decile_mask]
            
            income_change = scenario_subset["disposable_income"] - baseline_subset["disposable_income"]
            
            decile_stats = {
                "decile": decile,
                "population": len(baseline_subset),
                "baseline_mean_income": baseline_subset["disposable_income"].mean(),
                "scenario_mean_income": scenario_subset["disposable_income"].mean(),
                "mean_change": income_change.mean(),
                "median_change": income_change.median(),
                "pct_better_off": (income_change > 0).sum() / len(income_change) * 100,
                "pct_worse_off": (income_change < 0).sum() / len(income_change) * 100,
                "max_gain": income_change.max(),
                "max_loss": income_change.min(),
            }
            
            decile_analysis.append(decile_stats)
        
        return pd.DataFrame(decile_analysis)
    
    def generate_demographic_analysis(self) -> Dict[str, pd.DataFrame]:
        """Analyze impact by demographic groups if data is available."""
        
        demographic_results = {}
        
        # Analyze by age groups if age column exists
        if "age" in self.baseline_data.columns:
            age_groups = {
                "18-25": (18, 25),
                "26-35": (26, 35), 
                "36-45": (36, 45),
                "46-55": (46, 55),
                "56-65": (56, 65),
                "65+": (65, 100)
            }
            
            age_analysis = []
            for group_name, (min_age, max_age) in age_groups.items():
                mask = (self.baseline_data["age"] >= min_age) & (self.baseline_data["age"] <= max_age)
                
                if mask.sum() > 0:  # Only include if there are people in this age group
                    baseline_subset = self.baseline_data[mask]
                    scenario_subset = self.scenario_data[mask]
                    
                    income_change = scenario_subset["disposable_income"] - baseline_subset["disposable_income"]
                    
                    age_stats = {
                        "age_group": group_name,
                        "population": len(baseline_subset),
                        "mean_change": income_change.mean(),
                        "median_change": income_change.median(),
                        "pct_better_off": (income_change > 0).sum() / len(income_change) * 100
                    }
                    age_analysis.append(age_stats)
            
            demographic_results["age_groups"] = pd.DataFrame(age_analysis)
        
        # Analyze by family structure if relevant columns exist
        if "adults" in self.baseline_data.columns and "children" in self.baseline_data.columns:
            family_analysis = []
            
            family_types = {
                "Single, no children": (1, 0),
                "Single parent": (1, ">=1"), 
                "Couple, no children": (2, 0),
                "Couple with children": (2, ">=1")
            }
            
            for family_type, (adults, children) in family_types.items():
                if children == ">=1":
                    mask = (self.baseline_data["adults"] == adults) & (self.baseline_data["children"] >= 1)
                else:
                    mask = (self.baseline_data["adults"] == adults) & (self.baseline_data["children"] == children)
                
                if mask.sum() > 0:
                    baseline_subset = self.baseline_data[mask]
                    scenario_subset = self.scenario_data[mask]
                    
                    income_change = scenario_subset["disposable_income"] - baseline_subset["disposable_income"]
                    
                    family_stats = {
                        "family_type": family_type,
                        "population": len(baseline_subset),
                        "mean_change": income_change.mean(),
                        "median_change": income_change.median(),
                        "pct_better_off": (income_change > 0).sum() / len(income_change) * 100
                    }
                    family_analysis.append(family_stats)
            
            demographic_results["family_types"] = pd.DataFrame(family_analysis)
        
        return demographic_results
    
    def generate_markdown_report(self, output_path: Optional[str] = None) -> str:
        """Generate a comprehensive markdown report."""
        
        summary = self.generate_executive_summary()
        decile_analysis = self.generate_decile_analysis()
        demographic_analysis = self.generate_demographic_analysis()
        
        # Markdown template
        template_str = '''
# Policy Analysis Report: {{ summary.scenario_name }}

**Analysis Date:** {{ summary.analysis_date }}  
**Baseline:** {{ summary.baseline_name }}  
**Total Population:** {{ "{:,.0f}"|format(summary.total_population) }} individuals

## Executive Summary

### Key Findings

{% if summary.gini_change > 0 %}
- **Inequality increases** by {{ "{:.3f}"|format(summary.gini_change) }} Gini points ({{ "{:+.1f}"|format(summary.gini_pct_change) }}%)
{% else %}
- **Inequality decreases** by {{ "{:.3f}"|format(-summary.gini_change) }} Gini points ({{ "{:+.1f}"|format(summary.gini_pct_change) }}%)
{% endif %}

{% if summary.poverty_change > 0 %}
- **Poverty rate increases** by {{ "{:+.1f}"|format(summary.poverty_pct_change) }}%
{% else %}
- **Poverty rate decreases** by {{ "{:.1f}"|format(-summary.poverty_pct_change) }} percentage points
{% endif %}

- **{{ "{:,.0f}"|format(summary.winners) }}** individuals ({{ "{:.1f}"|format(summary.winners_pct) }}%) are better off by more than $50
- **{{ "{:,.0f}"|format(summary.losers) }}** individuals ({{ "{:.1f}"|format(summary.losers_pct) }}%) are worse off by more than $50

### Fiscal Impact

- **Tax Revenue Change:** {{ "${:+,.0f}"|format(summary.tax_revenue_change) }}
- **Transfer Change:** {{ "${:+,.0f}"|format(summary.transfer_change) }}  
- **Net Fiscal Impact:** {{ "${:+,.0f}"|format(summary.net_fiscal_impact) }}

### Income Impact

- **Median Income Change:** {{ "${:+,.0f}"|format(summary.median_income_change) }}
- **Mean Income Change:** {{ "${:+,.0f}"|format(summary.mean_income_change) }}

## Distributional Analysis by Income Decile

| Decile | Population | Baseline Mean Income | Mean Change | % Better Off | % Worse Off |
|--------|------------|---------------------|-------------|--------------|-------------|
{% for _, row in decile_analysis.iterrows() -%}
| {{ row.decile }} | {{ "{:,.0f}"|format(row.population) }} | {{ "${:,.0f}"|format(row.baseline_mean_income) }} | {{ "${:+,.0f}"|format(row.mean_change) }} | {{ "{:.1f}%"|format(row.pct_better_off) }} | {{ "{:.1f}%"|format(row.pct_worse_off) }} |
{% endfor %}

{% if demographic_analysis.age_groups is defined %}
## Analysis by Age Groups

| Age Group | Population | Mean Change | % Better Off |
|-----------|------------|-------------|--------------|
{% for _, row in demographic_analysis.age_groups.iterrows() -%}
| {{ row.age_group }} | {{ "{:,.0f}"|format(row.population) }} | {{ "${:+,.0f}"|format(row.mean_change) }} | {{ "{:.1f}%"|format(row.pct_better_off) }} |
{% endfor %}
{% endif %}

{% if demographic_analysis.family_types is defined %}
## Analysis by Family Type

| Family Type | Population | Mean Change | % Better Off |
|-------------|------------|-------------|--------------|
{% for _, row in demographic_analysis.family_types.iterrows() -%}
| {{ row.family_type }} | {{ "{:,.0f}"|format(row.population) }} | {{ "${:+,.0f}"|format(row.mean_change) }} | {{ "{:.1f}%"|format(row.pct_better_off) }} |
{% endfor %}
{% endif %}

## Methodology

This analysis compares the distributional and fiscal impacts of the proposed policy scenario against the current policy baseline. 

- **Gini coefficient** measures income inequality (0 = perfect equality, 1 = perfect inequality)
- **Poverty rate** is calculated using 60% of median income as the poverty line
- **Income deciles** are based on baseline disposable income distribution
- **Better/worse off** is defined as income changes greater than $50 in absolute value

---
*Generated by NZ Tax Microsimulation Model on {{ summary.analysis_date }}*
'''
        
        template = Template(template_str)
        report_content = template.render(
            summary=summary,
            decile_analysis=decile_analysis,
            demographic_analysis=demographic_analysis
        )
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(report_content)
        
        return report_content
    
    def generate_charts(self, output_dir: str) -> List[str]:
        """Generate standard charts for the report."""
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)
        
        chart_files = []
        
        # Set up matplotlib style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # 1. Income distribution comparison
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        ax1.hist(self.baseline_data["disposable_income"], bins=50, alpha=0.7, label=self.baseline_name)
        ax1.hist(self.scenario_data["disposable_income"], bins=50, alpha=0.7, label=self.scenario_name)
        ax1.set_xlabel("Disposable Income ($)")
        ax1.set_ylabel("Frequency")
        ax1.set_title("Income Distribution Comparison")
        ax1.legend()
        
        # 2. Income change by decile
        decile_analysis = self.generate_decile_analysis()
        ax2.bar(decile_analysis["decile"], decile_analysis["mean_change"])
        ax2.set_xlabel("Income Decile")
        ax2.set_ylabel("Mean Income Change ($)")
        ax2.set_title("Average Income Change by Decile")
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        plt.tight_layout()
        chart_file = output_path / "income_analysis.png"
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        chart_files.append(str(chart_file))
        plt.close()
        
        # 3. Winners and losers analysis
        income_diff = self.scenario_data["disposable_income"] - self.baseline_data["disposable_income"]
        
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        ax.hist(income_diff, bins=100, alpha=0.7, color='steelblue')
        ax.axvline(x=0, color='red', linestyle='--', label='No change')
        ax.set_xlabel("Income Change ($)")
        ax.set_ylabel("Number of Individuals")
        ax.set_title("Distribution of Income Changes")
        ax.legend()
        
        chart_file = output_path / "income_changes.png"
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        chart_files.append(str(chart_file))
        plt.close()
        
        return chart_files


def generate_comparison_report(scenarios: Dict[str, pd.DataFrame], 
                             output_dir: str = "reports") -> str:
    """
    Generate a multi-scenario comparison report.
    
    Args:
        scenarios: Dictionary mapping scenario names to result DataFrames
        output_dir: Directory to save the report and charts
        
    Returns:
        Path to the generated report file
    """
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True, parents=True)
    
    # Generate comparison table
    comparison_data = []
    
    for scenario_name, df in scenarios.items():
        stats = {
            "Scenario": scenario_name,
            "Gini Coefficient": calculate_gini_coefficient(df["disposable_income"]),
            "Poverty Rate (%)": calculate_poverty_rate(df, threshold=0.6) * 100,
            "Mean Income": df["disposable_income"].mean(),
            "Median Income": df["disposable_income"].median(),
            "Total Tax Revenue": calculate_total_tax_revenue(df),
            "Total Transfers": calculate_total_welfare_transfers(df),
        }
        comparison_data.append(stats)
    
    comparison_df = pd.DataFrame(comparison_data)
    
    # Generate markdown report
    report_content = f"""
# Multi-Scenario Policy Comparison

**Generated:** {datetime.datetime.now().strftime("%B %d, %Y")}

## Summary Comparison

{comparison_df.to_markdown(index=False, floatfmt='.2f')}

## Key Insights

### Inequality Impact
- **Lowest Gini:** {comparison_df.loc[comparison_df['Gini Coefficient'].idxmin(), 'Scenario']} ({comparison_df['Gini Coefficient'].min():.3f})
- **Highest Gini:** {comparison_df.loc[comparison_df['Gini Coefficient'].idxmax(), 'Scenario']} ({comparison_df['Gini Coefficient'].max():.3f})

### Poverty Impact  
- **Lowest Poverty Rate:** {comparison_df.loc[comparison_df['Poverty Rate (%)'].idxmin(), 'Scenario']} ({comparison_df['Poverty Rate (%)'].min():.1f}%)
- **Highest Poverty Rate:** {comparison_df.loc[comparison_df['Poverty Rate (%)'].idxmax(), 'Scenario']} ({comparison_df['Poverty Rate (%)'].max():.1f}%)

### Fiscal Impact
- **Highest Tax Revenue:** {comparison_df.loc[comparison_df['Total Tax Revenue'].idxmax(), 'Scenario']} (${comparison_df['Total Tax Revenue'].max():,.0f})
- **Highest Transfer Spending:** {comparison_df.loc[comparison_df['Total Transfers'].idxmax(), 'Scenario']} (${comparison_df['Total Transfers'].max():,.0f})

---
*Generated by NZ Tax Microsimulation Model*
"""
    
    report_file = output_path / "multi_scenario_comparison.md"
    with open(report_file, 'w') as f:
        f.write(report_content)
    
    return str(report_file)