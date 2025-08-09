"""Rules for the Working for Families tax credit simulation."""

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class GrossUpIncomeRule:
    """Rule to gross up income for WFF calculation."""

    name: str = "gross_up_income"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        """Applies the gross-up logic to the family income."""
        df = data["df"]
        # This is a placeholder for the actual logic.
        df["wff_income"] = df["familyinc"] * 1.0  # Example


@dataclass
class CalculateMaxEntitlementsRule:
    """Rule to calculate maximum WFF entitlements."""

    name: str = "calculate_max_entitlements"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculates the maximum entitlements for each component of WFF."""
        df = data["df"]
        # Placeholder for detailed logic
        df["max_ftc"] = 1000  # Example values
        df["max_iwc"] = 500
        df["max_bstc"] = 300
        df["max_mftc"] = 2000


@dataclass
class ApplyCareLogicRule:
    """Rule to apply shared care logic."""

    name: str = "apply_care_logic"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        """Adjusts entitlements based on shared care arrangements."""
        df = data["df"]
        # Placeholder for logic
        df.loc[df["sharedcare"] == 1, "max_ftc"] *= 0.5


@dataclass
class CalculateAbatementRule:
    """Rule to calculate the abatement of WFF entitlements."""

    name: str = "calculate_abatement"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculates the abatement based on family income."""
        df = data["df"]
        abatement_threshold = 42700
        abatement_rate = 0.27
        df["abatement"] = np.maximum(0, (df["wff_income"] - abatement_threshold) * abatement_rate)


@dataclass
class ApplyCalibrationsRule:
    """Rule to apply calibrations to WFF results."""

    name: str = "apply_calibrations"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        """Applies calibration factors to the final WFF entitlements."""
        df = data["df"]
        # Placeholder for calibration logic
        calibration_factor = 1.0  # Example factor
        df["final_wff_entitlement"] = df.get("final_wff_entitlement", 0) * calibration_factor


@dataclass
class CalculateFinalEntitlementsRule:
    """Rule to calculate the final WFF entitlements."""

    name: str = "calculate_final_entitlements"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculates the final WFF entitlements."""
        df = data["df"]
        df["FTCcalc"] = np.maximum(0, df["max_ftc"] - df["abatement"])
        df["IWTCcalc"] = np.maximum(0, df["max_iwc"] - df["abatement"])
        df["BSTCcalc"] = np.maximum(0, df["max_bstc"] - df["abatement"])
        df["MFTCcalc"] = np.maximum(0, df["max_mftc"] - df["abatement"])
