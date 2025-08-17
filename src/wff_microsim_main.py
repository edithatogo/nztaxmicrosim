import pandas as pd

from src.reporting import generate_microsim_report
from src.tax_calculator import TaxCalculator
from src.validation import SimulationInputSchema, validate_input_data


def main() -> None:
    """
    This is the main entry point for the Working for Families (WFF) microsimulation model.
    It demonstrates how to load parameters, create a sample DataFrame, and run the `famsim`
    function to calculate WFF entitlements. The results are then printed to the console.
    """
    # Load the data
    # df = pd.read_csv('data.csv')

    # For now, create a sample dataframe
    df: pd.DataFrame = pd.DataFrame(
        {
            # Core Demographics & Household Characteristics
            "person_id": [1, 2, 3],
            "household_id": [1, 2, 3],
            "age": [35, 40, 28],
            "gender": ["Female", "Male", "Female"],
            "marital_status": ["Married", "Married", "Single"],
            "family_household_type": ["Couple with children", "Couple with children", "Single adult"],
            "household_size": [4, 4, 1],
            "num_children": [2, 2, 0],
            "adults": [2, 2, 1],
            "ages_of_children": [[5, 8], [2, 6], []],  # Example: list of ages
            "region": ["Auckland", "Wellington", "Christchurch"],
            "disability_status": [False, False, True],
            # Core Income and Employment Variables
            "employment_income": [45000, 90000, 25000],
            "self_employment_income": [5000, 10000, 0],
            "investment_income": [500, 2000, 100],
            "rental_property_income": [0, 0, 0],
            "private_pensions_annuities": [0, 0, 0],
            "employment_status": ["Employed", "Employed", "Unemployed"],
            "hours_worked": [40, 40, 0],
            # Core Government Transfers Received (Input flags)
            "is_jss_recipient": [False, False, True],
            "is_sps_recipient": [False, False, False],
            "is_slp_recipient": [False, False, False],
            "is_nz_super_recipient": [False, False, False],
            # Core Housing Costs
            "housing_costs": [400, 500, 250],  # Weekly costs
            # Existing WFF-related columns (ensure consistency)
            "familyinc": [50000, 100000, 30000],
            "FTCwgt": [1, 1, 0],
            "IWTCwgt": [1, 1, 0],
            "BSTC0wgt": [1, 0, 0],
            "BSTC01wgt": [0, 1, 0],
            "BSTC1wgt": [0, 0, 1],
            "MFTCwgt": [1, 0, 0],
            "iwtc_elig": [1, 1, 0],
            "MFTC_total": [1000, 1000, 1000],
            "MFTC_elig": [1, 1, 1],
            "sharedcare": [0, 1, 0],
            "sharecareFTCwgt": [0, 1, 0],
            "sharecareBSTC0wgt": [0, 0, 0],
            "sharecareBSTC01wgt": [0, 1, 0],
            "sharecareBSTC1wgt": [0, 0, 0],
            "iwtc": [1, 1, 0],
            "selfempind": [0, 1, 0],
            "maxkiddays": [365, 365, 365],
            "maxkiddaysbstc": [365, 365, 365],
        }
    )

    # Compute household size fields required for validation
    df["pplcnt"] = df["num_children"] + df["adults"]

    # Validate inputs against the schema
    schema_cols = list(SimulationInputSchema.model_fields.keys())
    try:
        validated_subset = validate_input_data(df[schema_cols])
        df.update(validated_subset)
    except ValueError as e:
        print(f"Input data validation failed: {e}")
        return

    # Set the parameters for a specific year
    year = "2023-2024"
    from .microsim import load_parameters

    params = load_parameters(year)
    tax_calc = TaxCalculator(params=params)

    # Calculate total individual income (weekly for benefits)
    df["total_individual_income_weekly"] = (
        df["employment_income"] + df["self_employment_income"] + df["investment_income"]
    ) / 52

    from .pipeline import SimulationPipeline

    # Create the pipeline from the configuration file
    pipeline = SimulationPipeline.from_config("conf/pipeline.yml")

    # The pipeline needs access to the dataframe, params, and calculator
    data_context = {"df": df.copy(), "params": params, "tax_calc": tax_calc}
    result_data = pipeline.run(data_context)
    result = result_data["df"]

    # Calculate disposable income and AHC and add to result DataFrame
    result["disposable_income"] = (
        result["employment_income"]
        + result["self_employment_income"]
        + result["investment_income"]
        + result["rental_property_income"]
        + result["private_pensions_annuities"]
        + result["jss_entitlement"] * 52
        + result["sps_entitlement"] * 52
        + result["slp_entitlement"] * 52
        + result["accommodation_supplement_entitlement"] * 52
        + result["FTCcalc"]
        + result["IWTCcalc"]
        + result["BSTCcalc"]
        + result["MFTCcalc"]
        - result["tax_liability"]
        - result["acc_levy"]
        - result["kiwisaver_contribution"]
        - result["student_loan_repayment"]
    )
    result["disposable_income_ahc"] = result["disposable_income"] - (result["housing_costs"] * 52)

    # Ensure 'age' column is in the result DataFrame
    if "age" not in result.columns:
        result["age"] = df["age"]  # Assuming age is in the original df and aligns

    # Generate comprehensive report
    report_params = {
        "poverty_line_relative": 0.5  # Example: 50% of median income for poverty line
    }
    generate_microsim_report(result, report_params)


if __name__ == "__main__":
    main()
