"""
This module provides functionality for modelling behavioural responses to
policy changes, such as labour supply responses.
"""

<<<<<<< HEAD
import numpy as np
import pandas as pd

=======
import pandas as pd
import numpy as np
>>>>>>> origin/update-a-bunch-of-stuff-5

def labour_supply_response(
    df_before: pd.DataFrame,
    df_after: pd.DataFrame,
    emtr_calculator_before,
    emtr_calculator_after,
<<<<<<< HEAD
    elasticity_params: dict,
=======
    elasticity_params: dict
>>>>>>> origin/update-a-bunch-of-stuff-5
) -> pd.DataFrame:
    """
    Simulates the labour supply response for a given population by comparing
    two scenarios (e.g., before and after a policy reform).

    This function adjusts the 'income' of individuals based on changes to their
    Effective Marginal Tax Rate (EMTR) and net income, using a set of
    elasticity parameters. This implementation focuses on the intensive margin.

    Args:
        df_before: The population DataFrame under the baseline policy.
        df_after: The population DataFrame under the reform policy.
        emtr_calculator_before: An instance of the TaxCalculator for the baseline.
        emtr_calculator_after: An instance of the TaxCalculator for the reform.
        elasticity_params: A dictionary of elasticity parameters, e.g.,
            {
                "primary_earner_intensive_margin": 0.1,
                "secondary_earner_intensive_margin": 0.3
            }

    Returns:
        A new DataFrame with adjusted income values reflecting the labour
        supply response.
    """
    print("Simulating labour supply response...")

    # Ensure dataframes are aligned
    if not df_before.index.equals(df_after.index):
        raise ValueError("Input DataFrames must have the same index.")

    df_behavioural = df_after.copy()

    # --- 1. Calculate EMTRs and Net Incomes for both scenarios ---

    # Note: This is computationally intensive as it iterates row by row.
    # Vectorized approaches would be faster but more complex to implement.

<<<<<<< HEAD
    emtr_before = df_before.apply(lambda row: emtr_calculator_before.calculate_emtr(row.to_dict()), axis=1)
    df_before.apply(
        lambda row: emtr_calculator_before._calculate_net_income(row.to_dict()),
        axis=1,
    )

    emtr_after = df_after.apply(lambda row: emtr_calculator_after.calculate_emtr(row.to_dict()), axis=1)
    df_after.apply(lambda row: emtr_calculator_after._calculate_net_income(row.to_dict()), axis=1)
=======
    emtr_before = df_before.apply(
        lambda row: emtr_calculator_before.calculate_emtr(row.to_dict()), axis=1
    )
    net_income_before = df_before.apply(
        lambda row: emtr_calculator_before._calculate_net_income(row.to_dict()), axis=1
    )

    emtr_after = df_after.apply(
        lambda row: emtr_calculator_after.calculate_emtr(row.to_dict()), axis=1
    )
    net_income_after = df_after.apply(
        lambda row: emtr_calculator_after._calculate_net_income(row.to_dict()), axis=1
    )
>>>>>>> origin/update-a-bunch-of-stuff-5

    # --- 2. Determine primary/secondary earners (simple heuristic) ---
    # In a family, the person with the higher income is the primary earner.
    # This assumes a 'family_id' and 'income' column exist.
<<<<<<< HEAD
    if "family_id" in df_before.columns and "income" in df_before.columns:
        df_before["is_primary_earner"] = df_before.groupby("family_id")["income"].transform(lambda x: x == x.max())
    else:
        # If no family structure, assume everyone is a primary earner.
        df_before["is_primary_earner"] = True
=======
    if 'family_id' in df_before.columns and 'income' in df_before.columns:
        df_before['is_primary_earner'] = df_before.groupby('family_id')['income'].transform(lambda x: x == x.max())
    else:
        # If no family structure, assume everyone is a primary earner.
        df_before['is_primary_earner'] = True
>>>>>>> origin/update-a-bunch-of-stuff-5

    # --- 3. Calculate the change in labour supply ---

    # The change in the net-of-tax rate (1 - EMTR) drives the substitution effect.
    change_in_log_net_wage = np.log(1 - emtr_after) - np.log(1 - emtr_before)

    # The change in net income drives the income effect.
    # A simple assumption is that the income effect is proportional to elasticity.
    # For this version, we focus on the substitution effect which is standard.

    elasticities = np.where(
<<<<<<< HEAD
        df_before["is_primary_earner"],
        elasticity_params.get("primary_earner_intensive_margin", 0.1),
        elasticity_params.get("secondary_earner_intensive_margin", 0.3),
=======
        df_before['is_primary_earner'],
        elasticity_params.get("primary_earner_intensive_margin", 0.1),
        elasticity_params.get("secondary_earner_intensive_margin", 0.3)
>>>>>>> origin/update-a-bunch-of-stuff-5
    )

    # Percentage change in hours worked (and thus labour income)
    pct_change_in_labour_supply = elasticities * change_in_log_net_wage

    # --- 4. Apply the change to income ---
    # We adjust the 'income' column. This assumes most income is from labour.
    # A more advanced model would distinguish between labour and capital income.
<<<<<<< HEAD
    df_behavioural["income"] = df_behavioural["income"] * (1 + pct_change_in_labour_supply)
=======
    df_behavioural['income'] = df_behavioural['income'] * (1 + pct_change_in_labour_supply)
>>>>>>> origin/update-a-bunch-of-stuff-5

    print("Labour supply response simulation complete.")
    return df_behavioural
