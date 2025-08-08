import numpy as np
import pandas as pd

from .parameters import WFFParams
from .rules_engine import Rule, RuleEngine


def famsim(
    df: pd.DataFrame,
    wff_params: WFFParams,
    wagegwt: float,
    daysinperiod: int,
) -> pd.DataFrame:
    """Compose the WFF calculation phases using a rule engine.

    Args:
        df: DataFrame containing family information.
        wff_params: Working for Families parameters.
        wagegwt: Wage growth rate.
        daysinperiod: Number of days in the period.

    Returns:
        DataFrame with calculated WFF entitlements.
    """
    engine = RuleEngine(
        [
            Rule("gross_up_income", gross_up_income, {"wagegwt": wagegwt}),
            Rule(
                "calculate_abatement",
                calculate_abatement,
                {"wff_params": wff_params, "daysinperiod": daysinperiod},
            ),
            Rule(
                "calculate_max_entitlements",
                calculate_max_entitlements,
                {"wff_params": wff_params},
            ),
            Rule(
                "apply_care_logic",
                apply_care_logic,
                {"wff_params": wff_params},
            ),
            Rule("apply_calibrations", apply_calibrations),
        ]
    )

    return engine.run(df.copy())
