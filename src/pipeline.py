"""Simple plug-in pipeline for orchestrating tax and benefit rules."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from .tax_calculator import TaxCalculator


class Rule(Protocol):
    """Protocol for a simulation rule.

    Rules have a ``name`` used for identification, an ``enabled`` flag to
    control execution and are callable with a single ``data`` argument that is
    mutated in-place.
    """

    name: str
    enabled: bool

    def __call__(self, data: dict[str, Any]) -> None:  # pragma: no cover - Protocol
        ...


import yaml

@dataclass
class SimulationPipeline:
    """Sequentially execute enabled rules to update a simulation ``state``."""

    rules: list[Rule] = field(default_factory=list)

    @classmethod
    def from_config(cls, config_path: str, params: dict[str, Any]) -> "SimulationPipeline":
        """Create a SimulationPipeline from a YAML configuration file."""
        with open(config_path) as f:
            config = yaml.safe_load(f)

        rules = []
        for rule_config in config["rules"]:
            rule_name = rule_config["name"]
            # Note: This is a simple factory. For more complex rules, you might need a more robust mechanism.
            if rule_name == "IncomeTaxRule":
                rules.append(IncomeTaxRule(calculator=TaxCalculator(params=params)))
            elif rule_name == "IETCRule":
                rules.append(IETCRule(calculator=TaxCalculator(params=params)))
            # Add other rules here as they are created
        return cls(rules)

    def _find_rule_index(self, name: str) -> int | None:
        """Find the index of a rule by name."""
        for i, rule in enumerate(self.rules):
            if rule.name == name:
                return i
        return None

    def run(self, data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Run all enabled rules sequentially."""
        if data is None:
            data = {}
        for rule in self.rules:
            if getattr(rule, "enabled", True):
                rule(data)
        return data

    def enable(self, name: str) -> None:
        """Enable the rule ``name`` if present."""
        if (idx := self._find_rule_index(name)) is not None:
            self.rules[idx].enabled = True

    def disable(self, name: str) -> None:
        """Disable the rule ``name`` if present."""
        if (idx := self._find_rule_index(name)) is not None:
            self.rules[idx].enabled = False

    def replace(self, name: str, new_rule: Rule) -> None:
        """Replace the rule ``name`` with ``new_rule``."""
        if (idx := self._find_rule_index(name)) is not None:
            self.rules[idx] = new_rule


@dataclass
class IncomeTaxRule:
    """Calculate income tax for the ``taxable_income`` field."""

    calculator: TaxCalculator
    name: str = "income_tax"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:  # pragma: no cover - simple
        df = data["df"]
        df["tax_liability"] = df["familyinc"].apply(self.calculator.income_tax)


@dataclass
class IETCRule:
    """Calculate the Independent Earner Tax Credit (IETC)."""

    calculator: TaxCalculator
    name: str = "ietc"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:  # pragma: no cover - simple
        df = data["df"]
        df["ietc"] = df.apply(
            lambda row: self.calculator.ietc(
                taxable_income=row["familyinc"],
                is_wff_recipient=row.get("is_wff_recipient", False),
                is_super_recipient=row.get("is_super_recipient", False),
                is_benefit_recipient=row.get("is_benefit_recipient", False),
            ),
            axis=1,
        )
