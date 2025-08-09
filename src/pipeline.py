"""Simple plug-in pipeline for orchestrating tax and benefit rules."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

import yaml

from .parameters import Parameters
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
    """A pipeline for running a series of simulation rules.

    The pipeline stores a list of rules and executes them sequentially on a
    given data dictionary. Rules can be enabled, disabled, or replaced.
    """

            rules: list[Rule] = []

    @classmethod
    def from_config(cls, config_path: str, params: dict[str, Any]) -> "SimulationPipeline":
        """Create a SimulationPipeline from a YAML configuration file.

        The configuration file should specify a list of rules to be included
        in the pipeline. This method provides a simple factory for creating
        the pipeline from the configuration.

        Args:
            config_path: The path to the YAML configuration file.
            params: A dictionary of parameters to be used by the rules.

        Returns:
            A new `SimulationPipeline` instance.
        """
        with open(config_path) as f:
            config = yaml.safe_load(f)

        rules: list[Rule] = []
        validated_params = Parameters.model_validate(params)
        for rule_config in config["rules"]:
            rule_name = rule_config["name"]
            # Note: This is a simple factory. For more complex rules, you might need a more robust mechanism.
            if rule_name == "IncomeTaxRule":
                rules.append(IncomeTaxRule(calculator=TaxCalculator(params=validated_params)))
            elif rule_name == "IETCRule":
                rules.append(IETCRule(calculator=TaxCalculator(params=validated_params)))
            # Add other rules here as they are created
        return cls(rules)

    def _find_rule_index(self, name: str) -> int | None:
        """Find the index of a rule by its name.

        Args:
            name: The name of the rule to find.

        Returns:
            The index of the rule, or `None` if the rule is not found.
        """
        for i, rule in enumerate(self.rules):
            if rule.name == name:
                return i
        return None

    def run(self, data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Run all enabled rules in the pipeline sequentially.

        Each rule is called with the `data` dictionary, which it can modify
        in-place.

        Args:
            data: The data dictionary to be processed by the rules. It is
                expected to contain a 'df' key with a pandas DataFrame.

        Returns:
            The modified data dictionary.
        """
        if data is None:
            data = {}
        for rule in self.rules:
            if getattr(rule, "enabled", True):
                rule(data)
        return data

    def enable(self, name: str) -> None:
        """Enable a rule in the pipeline.

        Args:
            name: The name of the rule to enable.
        """
        if (idx := self._find_rule_index(name)) is not None:
            self.rules[idx].enabled = True

    def disable(self, name: str) -> None:
        """Disable a rule in the pipeline.

        Args:
            name: The name of the rule to disable.
        """
        if (idx := self._find_rule_index(name)) is not None:
            self.rules[idx].enabled = False

    def replace(self, name: str, new_rule: Rule) -> None:
        """Replace a rule in the pipeline.

        Args:
            name: The name of the rule to replace.
            new_rule: The new rule to insert into the pipeline.
        """
        if (idx := self._find_rule_index(name)) is not None:
            self.rules[idx] = new_rule


@dataclass
class IncomeTaxRule:
    """A rule to calculate income tax.

    This rule uses the `TaxCalculator` to calculate the income tax for each
    individual in the DataFrame based on their `familyinc`.
    """

    calculator: TaxCalculator
    name: str = "income_tax"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculate income tax and add it to the DataFrame.

        This method applies the `income_tax` method of the `TaxCalculator`
        to the `familyinc` column of the DataFrame in the `data` dictionary
        and stores the result in a new `tax_liability` column.

        Args:
            data: The data dictionary, expected to contain a 'df' key with
                a pandas DataFrame.
        """
        df = data["df"]
        df["tax_liability"] = df["familyinc"].apply(self.calculator.income_tax)


@dataclass
class IETCRule:
    """A rule to calculate the Independent Earner Tax Credit (IETC).

    This rule uses the `TaxCalculator` to calculate the IETC for each
    individual in the DataFrame based on their income and benefit status.
    """

    calculator: TaxCalculator
    name: str = "ietc"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculate the IETC and add it to the DataFrame.

        This method applies the `ietc` method of the `TaxCalculator` to each
        row of the DataFrame in the `data` dictionary and stores the result
        in a new `ietc` column.

        Args:
            data: The data dictionary, expected to contain a 'df' key with
                a pandas DataFrame.
        """
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
