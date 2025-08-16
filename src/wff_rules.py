"""Rules for the Working for Families microsimulation."""

from dataclasses import dataclass
from typing import Any

from .pipeline import Rule, register_rule
from .wff_logic import (
    apply_calibrations,
    apply_care_logic,
    calculate_abatement,
    calculate_max_entitlements,
    gross_up_income,
)


@register_rule
@dataclass
class GrossUpIncomeRule(Rule):
    """A rule to gross up income by a wage growth factor."""

    name: str = "GrossUpIncomeRule"
    enabled: bool = True
    wagegwt: float = 0.0

    def __call__(self, data: dict[str, Any]) -> None:
        """Gross up income and update the DataFrame."""
        df = data["df"]
        data["df"] = gross_up_income(df, self.wagegwt)


@register_rule
@dataclass
class AbatementRule(Rule):
    """A rule to calculate WFF abatement."""

    name: str = "AbatementRule"
    enabled: bool = True
    daysinperiod: int = 365

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculate abatement and update the DataFrame."""
        df = data["df"]
        wff_params = data["params"].wff
        if wff_params:
            data["df"] = calculate_abatement(df, wff_params, self.daysinperiod)


@register_rule
@dataclass
class MaxEntitlementsRule(Rule):
    """A rule to calculate maximum WFF entitlements."""

    name: str = "MaxEntitlementsRule"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculate max entitlements and update the DataFrame."""
        df = data["df"]
        wff_params = data["params"].wff
        if wff_params:
            data["df"] = calculate_max_entitlements(df, wff_params)


@register_rule
@dataclass
class CareLogicRule(Rule):
    """A rule to apply WFF care logic."""

    name: str = "CareLogicRule"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        """Apply care logic and update the DataFrame."""
        df = data["df"]
        wff_params = data["params"].wff
        if wff_params:
            data["df"] = apply_care_logic(df, wff_params)


@register_rule
@dataclass
class CalibrationRule(Rule):
    """A rule to apply WFF calibrations."""

    name: str = "CalibrationRule"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        """Apply calibrations and update the DataFrame."""
        df = data["df"]
        data["df"] = apply_calibrations(df)
