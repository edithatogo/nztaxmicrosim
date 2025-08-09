import runpy
import filecmp
import os

def test_basic_usage_e2e():
    """
    Runs the basic_usage.py script and compares its output to a golden file.
    """
    # Run the script
    runpy.run_path('examples/basic_usage.py')

    # Compare the output to the golden file
    assert filecmp.cmp('basic_usage_output.txt', 'tests/golden_basic_usage.txt')

    # Clean up the generated file
    os.remove('basic_usage_output.txt')
