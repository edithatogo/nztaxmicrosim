import numpy as np
import pandas as pd

from .parameters import WFFParams
from .pipeline import SimulationPipeline
from .wff_rules import (
    ApplyCalibrationsRule,
    ApplyCareLogicRule,
    CalculateAbatementRule,
    CalculateMaxEntitlementsRule,
    GrossUpIncomeRule,
)


def famsim(
    df: pd.DataFrame,
    wff_params: WFFParams,
    wagegwt: float,
    daysinperiod: int,
) -> pd.DataFrame:
    """Compose the WFF calculation phases using a simulation pipeline.

    Args:
        df: DataFrame containing family information.
        wff_params: Structured WFF parameters.
        wagegwt: Wage growth rate.
        daysinperiod: Number of days in the period.

    Returns:
        DataFrame with calculated WFF entitlements.
    """
    pipeline = SimulationPipeline(
        [
            GrossUpIncomeRule(wagegwt=wagegwt),
            CalculateAbatementRule(
                wff_params=wff_params, daysinperiod=daysinperiod
            ),
            CalculateMaxEntitlementsRule(wff_params=wff_params),
            ApplyCareLogicRule(wff_params=wff_params),
            ApplyCalibrationsRule(),
        ]
    )

    result = pipeline.run({"df": df.copy()})
    return result["df"]
