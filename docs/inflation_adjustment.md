# Inflation Adjustment

The `src.inflation` module provides tools to adjust monetary values from different years into "real terms" against a common baseline year. This is essential for meaningful historical comparisons of policy impacts.

The module uses historical Consumer Price Index (CPI) data for New Zealand, fetched from the World Bank's data API.

## Key Functions

### `adjust_for_inflation()`

This is the main function for performing inflation adjustments.

::: src.inflation.adjust_for_inflation

## Usage Example

A full, working example of how to use this functionality can be found in the `examples/run_inflation_adjustment.py` script. Here is a brief overview of the process:

1.  **Prepare your data:** Start with a pandas DataFrame that contains the monetary data you wish to adjust.
2.  **Define parameters:** Specify your `base_year` (the year you want to convert *to*), your `target_year` (the year the data is currently *in*), and a list of the `columns_to_adjust`.
3.  **Call the function:** Pass your DataFrame and parameters to the `adjust_for_inflation()` function.

```python
# Example snippet from examples/run_inflation_adjustment.py

df_adjusted = adjust_for_inflation(
    data=my_dataframe,
    base_year=2022,
    target_year=1990,
    columns_to_adjust=["income", "assets"],
)
```

## Data Caching

The first time you use this module, it will download the necessary CPI data from the World Bank API. To improve performance on subsequent runs, this data is automatically cached in a `.cache` directory within the `src` folder. You can safely delete this directory if you need to force a re-download of the data.
