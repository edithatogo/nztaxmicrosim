# Historical Reporting Framework

The reporting framework has been extended to support multi-year historical analysis. This allows for the generation of reports that track key metrics over time, providing insights into the long-term effects of policy changes.

This framework is built upon the same `ReportComponent` architecture as the main reporting system but uses specialized components designed to handle data from multiple years.

## Configuration

Historical reports are driven by a YAML configuration file. This file allows you to specify which years to analyze, which reports to generate, and any specific parameters for those reports.

### Schema

Here is an overview of the configuration file structure:

*   `base_year_for_inflation` (integer): Optional. A baseline year for inflation adjustments. (Note: The reporting framework does not yet automatically apply this adjustment; it is for informational purposes).
*   `years_to_include` (list of integers): A list of the years you want to include in the analysis. The framework will expect to find corresponding data for each of these years.
*   `reports_to_generate` (list of strings): A list of the names of the historical report components to run.
*   `report_parameters` (dictionary): Optional. A dictionary where you can provide parameters for specific reports.

### Example Configuration

A full example can be found in `examples/historical_report_config.yml`.

```yaml
# examples/historical_report_config.yml
years_to_include:
  - 1990
  - 2000
  - 2010
  - 2020

reports_to_generate:
  - HistoricalGiniChart
  - HistoricalPovertyRateChart

report_parameters:
  poverty_rates_over_time:
    poverty_line_relative: 0.6
```

## Available Components

The following historical reporting components are available:

*   `HistoricalGiniChart`: Plots the Gini coefficient of disposable income over time.
*   `HistoricalPovertyRateChart`: Plots the poverty rate over time.
*   `HistoricalEffectiveTaxRateChart`: Plots the average effective tax rate over time.
*   `HistoricalBenefitEntitlementsChart`: Plots the average benefit entitlement per person over time.

## Usage Example

A full, working example of how to generate a report can be found in the `examples/run_historical_report.py` script. The script shows how to:
1.  Load the YAML configuration.
2.  Load or generate the data for the required years.
3.  Instantiate and run the reporting components.
4.  Compile the final report into a Markdown file.
