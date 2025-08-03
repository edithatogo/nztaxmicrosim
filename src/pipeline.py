"""Utilities for building modular simulation pipelines."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


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


@dataclass
class SimulationPipeline:
    """Execute a sequence of rules on shared ``data``."""

    rules: list[Rule]

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
            if rule.enabled:
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
