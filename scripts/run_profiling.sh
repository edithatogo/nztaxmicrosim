#!/bin/bash

# This script runs the performance profiling tests for the project.

# Exit immediately if a command exits with a non-zero status.
set -e

# Define the output file for the profile data
PROFILE_OUTPUT_DIR="prof"
PROFILE_OUTPUT_FILE="$PROFILE_OUTPUT_DIR/profile_$(date +%Y%m%d_%H%M%S).prof"

# Create the output directory if it doesn't exist
mkdir -p $PROFILE_OUTPUT_DIR

# Run the profiling
echo "Running performance profiling... output will be saved to $PROFILE_OUTPUT_FILE"
pytest --profile --profile-dump=$PROFILE_OUTPUT_FILE

echo "Profiling finished successfully."
