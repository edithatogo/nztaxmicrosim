# Historic Tax Search Plan

This document outlines a strategy for gathering New Zealand tax rules and
parameters for years prior to those already included in this repository.

## Data Sources

1. **data.govt.nz catalogue** – query the public dataset catalogue for
   entries related to "income tax" or "tax rates". Many resources hosted by
   Inland Revenue are indexed here and provide machine-readable files.
2. **Inland Revenue (ird.govt.nz)** – inspect resource links discovered
   via the catalogue for historical spreadsheets or CSV files, such as
   historic income tax rates.
3. **Legislation and government archives** – for years not covered by
   available datasets, consult legislative archives (e.g. via
   legislation.govt.nz) and historical government publications.

## Implementation Approach

The `historic_tax_search.py` utility automates the first step of this
plan. It queries the data.govt.nz API, lists dataset titles and
associated resource URLs, and can save results to disk for further
analysis. Subsequent work involves reviewing these resources and
converting relevant historical data into the repository's parameter
format.
