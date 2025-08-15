"""Rules for the Working for Families tax credit simulation."""

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from .pipeline import register_rule


@register_rule
@dataclass
class GrossUpIncomeRule:
    """Rule to gross up income for WFF calculation."""

    name: str = "gross_up_income"
    enabled: bool = True
    gross_up_factor: float = 1.0

    def __call__(self, data: dict[str, Any]) -> None:
        """Applies the gross-up logic to the family income."""
        df = data["df"]
        df["wff_income"] = df["familyinc"] * self.gross_up_factor


@register_rule
@dataclass
class CalculateMaxEntitlementsRule:
    """Rule to calculate maximum WFF entitlements."""

    name: str = "CalculateMaxEntitlementsRule"
    enabled: bool = True
    max_ftc: int = 1000
    max_iwc: int = 500
    max_bstc: int = 300
    max_mftc: int = 2000

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculates the maximum entitlements for each component of WFF."""
        df = data["df"]
        df["max_ftc"] = self.max_ftc
        df["max_iwc"] = self.max_iwc
        df["max_bstc"] = self.max_bstc
        df["max_mftc"] = self.max_mftc


@register_rule
@dataclass
class ApplyCareLogicRule:
    """Rule to apply shared care logic."""

    name: str = "ApplyCareLogicRule"
    enabled: bool = True
    shared_care_factor: float = 0.5

    def __call__(self, data: dict[str, Any]) -> None:
        """Adjusts entitlements based on shared care arrangements."""
        df = data["df"]
        df.loc[df.get("sharedcare", 0) == 1, "max_ftc"] *= self.shared_care_factor


@register_rule
@dataclass
class CalculateAbatementRule:
    """Rule to calculate the abatement of WFF entitlements."""

    name: str = "CalculateAbatementRule"
    enabled: bool = True
    abatement_threshold: int = 42700
    abatement_rate: float = 0.27

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculates the abatement based on family income."""
        df = data["df"]
        df["abatement"] = np.maximum(0, (df.get("wff_income", df["familyinc"]) - self.abatement_threshold) * self.abatement_rate)


@register_rule
@dataclass
class ApplyCalibrationsRule:
    """Rule to apply calibrations to WFF results."""

    name: str = "ApplyCalibrationsRule"
    enabled: bool = True
    calibration_factor: float = 1.0

    def __call__(self, data: dict[str, Any]) -> None:
        """Applies calibration factors to the final WFF entitlements."""
        df = data["df"]
        df["final_wff_entitlement"] = df.get("final_wff_entitlement", 0) * self.calibration_factor


@register_rule
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
