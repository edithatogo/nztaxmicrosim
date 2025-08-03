from dataclasses import dataclass
from typing import Any

from .parameters import WFFParams
from .pipeline import Rule
from .wff_logic import (
    apply_calibrations,
    apply_care_logic,
    calculate_abatement,
    calculate_max_entitlements,
    gross_up_income,
)


@dataclass
class GrossUpIncomeRule(Rule):
    """Rule to gross up family income."""

    wagegwt: float
    name: str = "gross_up_income"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        data["df"] = gross_up_income(data["df"], self.wagegwt)


@dataclass
class CalculateAbatementRule(Rule):
    """Rule to calculate WFF abatement."""

    wff_params: WFFParams
    daysinperiod: int
    name: str = "calculate_abatement"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        data["df"] = calculate_abatement(data["df"], self.wff_params, self.daysinperiod)


@dataclass
class CalculateMaxEntitlementsRule(Rule):
    """Rule to calculate maximum WFF entitlements."""

    wff_params: WFFParams
    name: str = "calculate_max_entitlements"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        data["df"] = calculate_max_entitlements(data["df"], self.wff_params)


@dataclass
class ApplyCareLogicRule(Rule):
    """Rule to apply shared and unshared care logic."""

    wff_params: WFFParams
    name: str = "apply_care_logic"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        data["df"] = apply_care_logic(data["df"], self.wff_params)


@dataclass
class ApplyCalibrationsRule(Rule):
    """Rule to apply model calibrations."""

    name: str = "apply_calibrations"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        data["df"] = apply_calibrations(data["df"])
