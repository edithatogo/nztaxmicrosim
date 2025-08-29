import filecmp
import os
import runpy
import sys


def run_example_script(script_name, args=None):
    """Helper function to run an example script and manage paths."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # Add project root to sys.path to allow imports like `from src.microsim...`
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    original_cwd = os.getcwd()
    os.chdir(project_root)  # Change to project root

    original_argv = sys.argv
    script_path = os.path.join("examples", script_name)
    sys.argv = [script_path] + (args or [])
    try:
        # The path to the script is relative to the project root
        runpy.run_path(script_path, run_name="__main__")
    finally:
        os.chdir(original_cwd)
        if project_root in sys.path:
            sys.path.remove(project_root)
        sys.argv = original_argv


def test_basic_usage_e2e():
    """
    Runs the basic_usage.py script and compares its output to a golden file.
    """
    output_file = "basic_usage_output.txt"
    if os.path.exists(output_file):
        os.remove(output_file)

    run_example_script("basic_usage.py")

    assert os.path.exists(output_file), f"{output_file} was not created."
    assert filecmp.cmp(output_file, "tests/golden_basic_usage.txt")
    os.remove(output_file)


def test_synthetic_population_e2e():
    """
    Runs the run_microsim_with_synthetic_population.py script and checks for output.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_file = os.path.join(
        project_root,
        "examples",
        "synthetic_population",
        "synthetic_population_results_2024-2025.csv",
    )
    if os.path.exists(output_file):
        os.remove(output_file)

    # Add the syspop directory to the path for this test
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    syspop_dir = os.path.join(project_root, "syspop")
    sys.path.insert(0, syspop_dir)

    try:
        run_example_script("run_microsim_with_synthetic_population.py", ["--population_scale", "0.01"])
    finally:
        sys.path.remove(syspop_dir)

    assert os.path.exists(output_file), f"{output_file} was not created."
    assert os.path.getsize(output_file) > 0
    os.remove(output_file)


def test_generate_reports_e2e():
    """
    Runs the generate_reports.py script and checks for the output directory.
    """
    output_dir = "reports"
    output_file = os.path.join(output_dir, "microsimulation_report.md")

    # Pre-create a dummy input file that the script expects
    os.makedirs("examples/synthetic_population", exist_ok=True)
    dummy_input_file = "examples/synthetic_population/synthetic_population_results_2024_2025.csv"
    with open(dummy_input_file, "w") as f:
        f.write(
            "person_id,income,taxable_income,familyinc,jss_entitlement,sps_entitlement,slp_entitlement,accommodation_supplement_entitlement,FTCcalc,IWTCcalc,BSTCcalc,MFTCcalc,income_tax_payable,employment_income,self_employment_income,investment_income,rental_property_income,private_pensions_annuities\n1,50000,50000,50000,0,0,0,0,0,0,0,0,8020,50000,0,0,0,0\n"
        )

    if os.path.exists(output_file):
        os.remove(output_file)
    if os.path.exists(output_dir) and not os.listdir(output_dir):
        os.rmdir(output_dir)

    # Modify sys.argv to pass the correct years parameter
    run_example_script("generate_reports.py", ["--years", "2024-2025"])

    assert os.path.exists(output_file), f"{output_file} was not created."
    assert os.path.getsize(output_file) > 0

    # Clean up
    os.remove(output_file)
    os.remove(dummy_input_file)
    if os.path.exists(output_dir) and not os.listdir(output_dir):
        os.rmdir(output_dir)
    if os.path.exists("examples/synthetic_population") and not os.listdir("examples/synthetic_population"):
        os.rmdir("examples/synthetic_population")


def test_policy_optimisation_e2e():
    """
    Runs the run_policy_optimisation.py script and checks for the output file.
    """
    output_file = "optimisation_results.csv"
    if os.path.exists(output_file):
        os.remove(output_file)

    # Pre-create a dummy input file that the script expects
    dummy_input_file = "puf.csv"
    with open(dummy_input_file, "w") as f:
        f.write(
            "person_id,income,taxable_income,familyinc,maxkiddays,maxkiddaysbstc,FTCwgt,IWTCwgt,iwtc_elig,BSTC0wgt,pplcnt,BSTC01wgt,BSTC1wgt,MFTC_total,MFTC_elig,sharedcare,sharecareFTCwgt,sharecareBSTC0wgt,sharecareBSTC01wgt,sharecareBSTC1wgt,MFTCwgt,iwtc,selfempind\n1,50000,50000,50000,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0\n"
        )

    run_example_script("run_policy_optimisation.py")

    assert os.path.exists(output_file), f"{output_file} was not created."
    assert os.path.getsize(output_file) > 0
    os.remove(output_file)
    os.remove(dummy_input_file)


def test_demographic_simulation_e2e():
    """
    Runs the run_demographic_simulation.py script and checks for the output file.
    """
    output_file = "demographic_simulation_results.csv"
    if os.path.exists(output_file):
        os.remove(output_file)

    run_example_script("run_demographic_simulation.py")

    assert os.path.exists(output_file), f"{output_file} was not created."
    assert os.path.getsize(output_file) > 0
    os.remove(output_file)
