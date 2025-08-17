"""Simple plug-in pipeline for orchestrating tax and benefit rules."""

from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from typing import Any

import yaml

from . import benefit_rules, tax_rules, wff_rules
from .rule_registry import RULE_REGISTRY, Rule


@dataclass
class SimulationPipeline:
    """A pipeline for running a series of simulation rules.

    The pipeline stores a list of rules and executes them sequentially on a
    given data dictionary. Rules can be enabled, disabled, or replaced.
    """

    rules: list[Rule] = field(default_factory=list)

    @classmethod
    def from_config(cls, config_path: str) -> "SimulationPipeline":
        """Create a SimulationPipeline from a YAML configuration file.

        The configuration file should specify a list of rules to be included
        in the pipeline. This method uses the RULE_REGISTRY to find and
        instantiate the rules. The rules are instantiated without parameters;
        they are expected to receive them from the `data` dictionary during
        the `run` phase.

        Args:
            config_path: The path to the YAML configuration file.

        Returns:
            A new `SimulationPipeline` instance.
        """
        with open(config_path) as f:
            config = yaml.safe_load(f)

        rules: list[Rule] = []

        # Import all rule modules to ensure they are registered

        for rule_config in config["rules"]:
            rule_name = rule_config.get("name") or rule_config.get("rule")
            if rule_name not in RULE_REGISTRY:
                # Fallback for old format
                if "." in rule_name:
                    module_path, class_name = rule_name.rsplit(".", 1)
                    try:
                        module = importlib.import_module(module_path)
                        rule_class = getattr(module, class_name)
                    except (ImportError, AttributeError):
                        raise ValueError(f"Unknown rule: {rule_name}")
                else:
                    raise ValueError(f"Unknown rule: {rule_name}")
            else:
                rule_class = RULE_REGISTRY[rule_name]

            # Rules are instantiated without arguments here.
            # They will get their data from the context dict passed to run().
            rules.append(rule_class())

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


# This file is now much simpler.
# The Rule Protocol and the SimulationPipeline class remain.
# The rule definitions have been moved to their respective modules.
# The from_config factory is simplified to only handle instantiation.
