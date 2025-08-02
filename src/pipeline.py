"""Simple plug-in pipeline for orchestrating tax and benefit rules."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from .tax_calculator import TaxCalculator


class Rule(Protocol):
    """Protocol for a single tax or benefit calculation module."""

    name: str
    enabled: bool

    def apply(self, state: dict[str, Any]) -> None:
        """Apply the rule to ``state`` modifying it in-place."""
        ...


@dataclass
class SimulationPipeline:
    """Sequentially execute enabled rules to update a simulation ``state``."""

    rules: list[Rule] = field(default_factory=list)

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Execute all enabled rules in order."""
        for rule in self.rules:
            if getattr(rule, "enabled", True):
                rule.apply(state)
        return state

    # Management helpers -------------------------------------------------

    def enable(self, name: str) -> None:
        """Enable the rule ``name`` if present."""
        for rule in self.rules:
            if rule.name == name:
                rule.enabled = True
                break

    def disable(self, name: str) -> None:
        """Disable the rule ``name`` if present."""
        for rule in self.rules:
            if rule.name == name:
                rule.enabled = False
                break

    def replace(self, name: str, new_rule: Rule) -> None:
        """Replace the rule ``name`` with ``new_rule``."""
        for idx, rule in enumerate(self.rules):
            if rule.name == name:
                self.rules[idx] = new_rule
                break


@dataclass
class IncomeTaxRule:
    """Calculate income tax for the ``taxable_income`` field."""

    calculator: TaxCalculator
    name: str = "income_tax"
    enabled: bool = True

    def apply(self, state: dict[str, Any]) -> None:  # pragma: no cover - simple
        income = state.get("taxable_income", 0.0)
        state["income_tax"] = self.calculator.income_tax(income)


@dataclass
class IETCRule:
    """Calculate the Independent Earner Tax Credit (IETC)."""

    calculator: TaxCalculator
    name: str = "ietc"
    enabled: bool = True

    def apply(self, state: dict[str, Any]) -> None:  # pragma: no cover - simple
        income = state.get("taxable_income", 0.0)
        state["ietc"] = self.calculator.ietc(
            taxable_income=income,
            is_wff_recipient=state.get("is_wff_recipient", False),
            is_super_recipient=state.get("is_super_recipient", False),
            is_benefit_recipient=state.get("is_benefit_recipient", False),
        )
