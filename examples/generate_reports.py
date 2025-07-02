import argparse
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.microsim import load_parameters


def generate_reports():
    """
    Loads the microsimulation results and generates a comprehensive set of
    reports, including tables and plots, with publication-quality formatting
    and natural language labels.
    """
    print("--- Generating Comprehensive Reports ---")

    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(description="Generate reports from microsimulation results.")
    parser.add_argument(
        "--param_files",
        nargs="+",
        type=str,
        default=["src/parameters.json"],
        help="Paths to the JSON files containing the tax parameters for different years.",
    )
    args = parser.parse_args()

    # --- Load Data and Parameters for each year ---
    all_dfs = {}
    for param_file in args.param_files:
        year = os.path.basename(param_file).split("_")[1].split(".")[0]

        results_filename = f"synthetic_population_results_{year}.csv"
        results_path = os.path.join("examples/synthetic_population", results_filename)

        if not os.path.exists(results_path):
            print(f"Error: Results file not found at {results_path} for year {year}")
            print("Please run 'run_microsim_with_synthetic_population.py' for this year first.")
            continue

        df_year = pd.read_csv(results_path)
        df_year["year"] = year  # Add a 'year' column for easy comparison
        all_dfs[year] = df_year

    if not all_dfs:
        print("No data loaded for reporting. Exiting.")
        return

    # Concatenate all dataframes for combined analysis
    df = pd.concat(all_dfs.values(), ignore_index=True)

    # Define abatement thresholds from parameters (using the first year's parameters for now)
    first_year_param_file = args.param_files[0]
    first_year = os.path.basename(first_year_param_file).split("_")[1].split(".")[0]
    first_year_params = load_parameters(first_year)
    abatethresh1 = first_year_params["wff"]["abatethresh1"]
    abatethresh2 = first_year_params["wff"]["abatethresh2"]
    bstcthresh = first_year_params["wff"]["bstcthresh"]

    # --- Create Reports Directory ---
    reports_dir = "examples/reports"
    os.makedirs(reports_dir, exist_ok=True)

    # --- Mapping for natural language labels ---
    column_labels = {
        "familyinc": "Family Income ($)",
        "age": "Age (Years)",
        "num_children": "Number of Children",
        "pplcnt": "Number of People in Family",
        "adults": "Number of Adults in Family",
        "FTCcalc": "Family Tax Credit ($)",
        "IWTCcalc": "In-Work Tax Credit ($)",
        "BSTCcalc": "Best Start Tax Credit ($)",
        "MFTCcalc": "Minimum Family Tax Credit ($)",
        "familyinc_grossed_up": "Grossed-Up Family Income ($)",
        "abate_amt": "Total Abatement Amount ($)",
        "BSTCabate_amt": "Best Start Tax Credit Abatement Amount ($)",
        "income_quintile": "Income Quintile",
        "total_wff_entitlement": "Total WFF Entitlement ($)",
        "income_tax_payable": "Income Tax Payable ($)",
        "ietc_amount": "Independent Earner Tax Credit ($)",
        "net_income": "Net Income ($)",
        "effective_tax_rate": "Effective Tax Rate (%)",
    }

    # Set plot style for publication quality
    sns.set_theme(style="whitegrid", palette="pastel")

    # --- I. Input Data Characteristics (Synthetic Population) ---
    print("\n### I. Input Data Characteristics (Synthetic Population)")

    # Tables
    print("\n#### Summary Statistics Table (Input Data)")
    input_summary_vars = ["familyinc", "age", "num_children", "pplcnt"]
    summary_input_df = df[input_summary_vars].describe().transpose()
    summary_input_df.index = [column_labels.get(col, col) for col in summary_input_df.index]
    print(summary_input_df.round(2).to_markdown())

    print("\n#### Frequency Distributions Table (Input Data)")
    for col in ["num_children", "adults"]:
        print(f"\n##### {column_labels.get(col, col)} Distribution")
        freq_table = df[col].value_counts(normalize=True).mul(100).round(2).to_frame(name="Percentage")
        freq_table["Count"] = df[col].value_counts()
        print(freq_table.to_markdown())

    # Plots
    print("\n#### Plots (Input Data)")
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    sns.histplot(data=df, x="familyinc", hue="year", kde=True, bins=30)
    plt.title("Distribution of Family Income by Year")
    plt.xlabel(column_labels["familyinc"])
    plt.ylabel("Frequency")

    plt.subplot(1, 2, 2)
    sns.histplot(data=df, x="age", hue="year", kde=True, bins=30)
    plt.title("Distribution of Age by Year")
    plt.xlabel(column_labels["age"])
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(os.path.join(reports_dir, "input_distribution_histograms_by_year.png"), dpi=300)
    plt.close()
    print(f"- Saved input_distribution_histograms_by_year.png to {reports_dir}")

    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    sns.countplot(data=df, x="num_children", hue="year", palette="viridis")
    plt.title("Number of Children Distribution by Year")
    plt.xlabel(column_labels["num_children"])
    plt.ylabel("Count")

    plt.subplot(1, 2, 2)
    sns.countplot(data=df, x="adults", hue="year", palette="viridis")
    plt.title("Number of Adults Distribution by Year")
    plt.xlabel(column_labels["adults"])
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(os.path.join(reports_dir, "input_categorical_bar_charts_by_year.png"), dpi=300)
    plt.close()
    print(f"- Saved input_categorical_bar_charts_by_year.png to {reports_dir}")

    # --- II. Output Data Characteristics (Calculated Entitlements) ---
    print("\n### II. Output Data Characteristics (Calculated Entitlements)")

    # Tables
    print("\n#### Summary Statistics Table (Output Data)")
    output_summary_vars = [
        "FTCcalc",
        "IWTCcalc",
        "BSTCcalc",
        "MFTCcalc",
        "familyinc_grossed_up",
        "abate_amt",
        "BSTCabate_amt",
    ]
    summary_output_df = df[output_summary_vars].describe().transpose()
    summary_output_df.index = [column_labels.get(col, col) for col in summary_output_df.index]
    print(summary_output_df.round(2).to_markdown())

    print("\n#### Total Entitlements Table")
    total_entitlements = df[["FTCcalc", "IWTCcalc", "BSTCcalc", "MFTCcalc"]].sum().to_frame(name="Total Amount")
    total_entitlements.index = [column_labels.get(col, col) for col in total_entitlements.index]
    print(total_entitlements.round(2).to_markdown())

    print("\n#### Participation Rates for WFF Components")
    participation_rates = (
        (df[["FTCcalc", "IWTCcalc", "BSTCcalc", "MFTCcalc"]] > 0)
        .mean()
        .mul(100)
        .to_frame(name="Participation Rate (%)")
    )
    participation_rates.index = [column_labels.get(col, col) for col in participation_rates.index]
    print(participation_rates.round(2).to_markdown())

    # Plots
    print("\n#### Plots (Output Data)")
    plt.figure(figsize=(15, 10))
    for i, col in enumerate(["FTCcalc", "IWTCcalc", "BSTCcalc", "MFTCcalc"]):
        plt.subplot(2, 2, i + 1)
        sns.histplot(data=df, x=col, hue="year", kde=True, bins=30)
        plt.title(f"Distribution of {column_labels.get(col, col)} by Year")
        plt.xlabel(column_labels.get(col, col))
        plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(os.path.join(reports_dir, "output_entitlement_histograms_by_year.png"), dpi=300)
    plt.close()
    print(f"- Saved output_entitlement_histograms_by_year.png to {reports_dir}")

    plt.figure(figsize=(15, 10))
    for i, col in enumerate(["FTCcalc", "IWTCcalc", "BSTCcalc", "MFTCcalc"]):
        plt.subplot(2, 2, i + 1)
        sns.boxplot(data=df, x="num_children", y=col, hue="year", palette="coolwarm")
        plt.title(f"{column_labels.get(col, col)} by Number of Children and Year")
        plt.xlabel(column_labels["num_children"])
        plt.ylabel(column_labels.get(col, col))
    plt.tight_layout()
    plt.savefig(os.path.join(reports_dir, "output_entitlement_box_plots_by_children_and_year.png"), dpi=300)
    plt.close()
    print(f"- Saved output_entitlement_box_plots_by_children_and_year.png to {reports_dir}")

    df["total_wff_entitlement"] = df["FTCcalc"] + df["IWTCcalc"] + df["BSTCcalc"] + df["MFTCcalc"]
    plt.figure(figsize=(8, 6))
    sns.histplot(data=df, x="total_wff_entitlement", hue="year", kde=True, bins=30, palette="dark:salmon_r")
    plt.title("Distribution of Total Working for Families Entitlement by Year")
    plt.xlabel(column_labels["total_wff_entitlement"])
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(os.path.join(reports_dir, "total_wff_entitlement_histogram_by_year.png"), dpi=300)
    plt.close()
    print(f"- Saved total_wff_entitlement_histogram_by_year.png to {reports_dir}")

    # --- III. Income Tax and Net Income Analysis ---
    print("\n### III. Income Tax and Net Income Analysis")

    # Tables
    print("\n#### Summary Statistics Table (Income Tax & Net Income)")
    income_tax_summary_vars = ["income_tax_payable", "net_income", "ietc_amount"]
    summary_income_tax_df = df[income_tax_summary_vars].describe().transpose()
    summary_income_tax_df.index = [column_labels.get(col, col) for col in summary_income_tax_df.index]
    print(summary_income_tax_df.round(2).to_markdown())

    print("\n#### Effective Tax Rate by Income Quintile")
    df["effective_tax_rate"] = (df["income_tax_payable"] / df["income"]).fillna(0) * 100
    df["income_quintile_individual"] = pd.qcut(
        df["income"],
        q=5,
        labels=[f"Q{i + 1}" for i in range(5)],
        duplicates="drop",
    )
    effective_tax_rate_report = (
        df.groupby("income_quintile_individual")["effective_tax_rate"]
        .mean()
        .to_frame(name="Average Effective Tax Rate (%)")
    )
    print(effective_tax_rate_report.round(2).to_markdown())

    # Plots
    print("\n#### Plots (Income Tax & Net Income)")
    plt.figure(figsize=(14, 6))
    plt.subplot(1, 2, 1)
    sns.histplot(data=df, x="income_tax_payable", hue="year", kde=True, bins=30, palette="dark:purple_r")
    plt.title("Distribution of Income Tax Payable by Year")
    plt.xlabel(column_labels["income_tax_payable"])
    plt.ylabel("Frequency")

    plt.subplot(1, 2, 2)
    sns.histplot(data=df, x="net_income", hue="year", kde=True, bins=30, palette="dark:blue_r")
    plt.title("Distribution of Net Income by Year")
    plt.xlabel(column_labels["net_income"])
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(os.path.join(reports_dir, "income_tax_net_income_histograms_by_year.png"), dpi=300)
    plt.close()
    print(f"- Saved income_tax_net_income_histograms_by_year.png to {reports_dir}")

    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x="income", y="income_tax_payable", hue="year", alpha=0.6, s=10, palette="dark:red_r")
    plt.title("Income Tax Payable vs. Gross Income by Year")
    plt.xlabel("Gross Income ($)")
    plt.ylabel(column_labels["income_tax_payable"])
    plt.ticklabel_format(style="plain", axis="x")
    plt.ticklabel_format(style="plain", axis="y")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(reports_dir, "income_tax_vs_income_scatter_by_year.png"), dpi=300)
    plt.close()
    print(f"- Saved income_tax_vs_income_scatter_by_year.png to {reports_dir}")

    # --- IV. Impact Analysis and Relationships (WFF) ---
    print("\n### IV. Impact Analysis and Relationships (WFF)")

    # Tables
    print("\n#### Average WFF Entitlements by Family Income Quintile")
    df["family_income_quintile"] = pd.qcut(
        df["familyinc_grossed_up"], q=5, labels=[f"Q{i + 1}" for i in range(5)], duplicates="drop"
    )
    wff_income_quintile_report_table = (
        df.groupby("family_income_quintile")[["FTCcalc", "IWTCcalc", "BSTCcalc", "MFTCcalc"]].mean().transpose()
    )
    wff_income_quintile_report_table.index = [
        column_labels.get(col, col) for col in wff_income_quintile_report_table.index
    ]
    print(wff_income_quintile_report_table.round(2).to_markdown())

    # Plots
    print("\n#### Scatter Plots with Abatement Visualization (WFF)")
    entitlement_cols = ["FTCcalc", "IWTCcalc", "BSTCcalc", "MFTCcalc"]
    for col in entitlement_cols:
        plt.figure(figsize=(10, 6))
        sns.scatterplot(x="familyinc_grossed_up", y=col, hue="year", data=df, alpha=0.6, s=10, palette="deep")
        plt.title(f"{column_labels.get(col, col)} vs. Grossed-Up Family Income by Year")
        plt.xlabel(column_labels["familyinc_grossed_up"])
        plt.ylabel(column_labels.get(col, col))
        plt.ticklabel_format(style="plain", axis="x")
        plt.ticklabel_format(style="plain", axis="y")

        # Plot abatement thresholds for the first year's parameters
        plt.axvline(
            x=abatethresh1,
            color="r",
            linestyle="--",
            label=f"Abatement Threshold 1 (${abatethresh1:,.0f}) (First Year)",
        )
        if col in ["FTCcalc", "IWTCcalc"]:
            plt.axvline(
                x=abatethresh2,
                color="purple",
                linestyle="--",
                label=f"Abatement Threshold 2 (${abatethresh2:,.0f}) (First Year)",
            )
        if col == "BSTCcalc":
            plt.axvline(
                x=bstcthresh,
                color="orange",
                linestyle="--",
                label=f"BSTC Abatement Threshold (${bstcthresh:,.0f}) (First Year)",
            )
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.savefig(os.path.join(reports_dir, f"{col.lower()}_vs_income_scatter_by_year.png"), dpi=300)
        plt.close()
        print(f"- Saved {col.lower()}_vs_income_scatter_by_year.png to {reports_dir}")

    # Plot: Average WFF Entitlements by Family Income Quintile
    wff_income_quintile_plot_data = (
        df.groupby(["family_income_quintile", "year"])[["FTCcalc", "IWTCcalc", "BSTCcalc", "MFTCcalc"]]
        .mean()
        .reset_index()
    )
    wff_income_quintile_plot_data = wff_income_quintile_plot_data.melt(
        id_vars=["family_income_quintile", "year"], var_name="WFF Component", value_name="Average Entitlement"
    )
    wff_income_quintile_plot_data["WFF Component"] = wff_income_quintile_plot_data["WFF Component"].apply(
        lambda x: column_labels.get(x, x)
    )
    plt.figure(figsize=(12, 7))
    sns.barplot(
        x="family_income_quintile",
        y="Average Entitlement",
        hue="WFF Component",
        data=wff_income_quintile_plot_data,
        palette="tab10",
        col="year",  # Create separate plots for each year
        col_wrap=2,
    )
    plt.suptitle("Average Working for Families Entitlements by Family Income Quintile and Year", y=1.02)
    plt.xlabel("Family Income Quintile")
    plt.ylabel("Average Entitlement ($)")
    plt.legend(title="WFF Component", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(os.path.join(reports_dir, "average_wff_entitlements_by_family_income_quintile_and_year.png"), dpi=300)
    plt.close()
    print(f"- Saved average_wff_entitlements_by_family_income_quintile_and_year.png to {reports_dir}")

    # --- V. Equity and Distributive Analysis ---
    print("\n### V. Equity and Distributive Analysis")

    # Calculate Net Disposable Income
    df["net_disposable_income"] = df["income"] + df["total_wff_entitlement"] - df["income_tax_payable"]

    def gini(arr):
        # from https://github.com/oliviaguest/gini
        # based on bottom eq: http://www.statsdirect.com/help/content/image/stat0206_wmf.gif
        # from http://www.statsdirect.com/help/default.htm#nonparametric_methods/gini.htm
        arr = np.array(arr)
        count = arr.size
        coefficient = 2.0 / count
        indexes = np.arange(1, count + 1)
        weighted_sum = (indexes * arr).sum()
        total = arr.sum()
        constant = (count + 1) / count
        return coefficient * weighted_sum / total - constant

    def lorenz_curve(X):
        X_lorenz = X.cumsum() / X.sum()
        X_lorenz = np.insert(X_lorenz, 0, 0)
        return X_lorenz

    # Gini Coefficient Analysis
    print("\n#### Gini Coefficient Analysis")
    gini_coefficients = (
        df.groupby("year")
        .apply(
            lambda x: pd.Series(
                {
                    "Market Income": gini(x["income"].values),
                    "Net Disposable Income": gini(x["net_disposable_income"].values),
                }
            )
        )
        .reset_index()
    )
    gini_coefficients = gini_coefficients.rename(columns={"index": "Year"})
    print(gini_coefficients.round(4).to_markdown(index=False))

    # Lorenz Curve Plot
    print("\n#### Lorenz Curve Plot")
    plt.figure(figsize=(8, 8))
    for year, df_year in all_dfs.items():
        market_income_lorenz = lorenz_curve(np.sort(df_year["income"].values))
        disposable_income_lorenz = lorenz_curve(np.sort(df_year["net_disposable_income"].values))
        plt.plot(np.linspace(0, 1, len(market_income_lorenz)), market_income_lorenz, label=f"Market Income ({year})")
        plt.plot(
            np.linspace(0, 1, len(disposable_income_lorenz)),
            disposable_income_lorenz,
            label=f"Net Disposable Income ({year})",
            linestyle="--",
        )

    plt.plot([0, 1], [0, 1], "k--", label="Line of Perfect Equality")
    plt.title("Lorenz Curves for Market and Net Disposable Income by Year")
    plt.xlabel("Cumulative Share of Population")
    plt.ylabel("Cumulative Share of Income")
    plt.legend()
    plt.axis("equal")
    plt.savefig(os.path.join(reports_dir, "lorenz_curves_by_year.png"), dpi=300)
    plt.close()
    print(f"- Saved lorenz_curves_by_year.png to {reports_dir}")

    print("\n--- Reporting Complete ---")


if __name__ == "__main__":
    generate_reports()

    print("\n--- Reporting Complete ---")


if __name__ == "__main__":
    generate_reports()
