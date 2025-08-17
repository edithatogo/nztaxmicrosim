#!/bin/bash

# This script runs the continuous integration checks for the project.

# Exit immediately if a command exits with a non-zero status.
set -e

# Run the test suite
echo "Running tests with tox..."
tox

# Run the data audit
echo "Running historical data audit..."
python scripts/audit_historical_data.py

echo "CI checks passed successfully."
