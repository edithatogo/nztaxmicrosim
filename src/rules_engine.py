from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List

import pandas as pd


@dataclass
class Rule:
    """A single transformation applied to a :class:`pandas.DataFrame`.

    Parameters
    ----------
    name:
        Human readable name for the rule.
    func:
        Callable that accepts a DataFrame as its first argument followed by
        any keyword arguments supplied via ``options``.
    options:
        Optional keyword arguments forwarded to ``func`` when the rule is
        executed.
    """

    name: str
    func: Callable[..., pd.DataFrame]
    options: Dict[str, Any] = field(default_factory=dict)

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply the rule to ``df`` and return the modified DataFrame."""
        return self.func(df, **self.options)


class RuleEngine:
    """Execute a sequence of :class:`Rule` objects in order."""

    def __init__(self, rules: Iterable[Rule] | None = None) -> None:
        self.rules: List[Rule] = list(rules) if rules is not None else []

    def add_rule(self, rule: Rule) -> None:
        """Append ``rule`` to the engine."""
        self.rules.append(rule)

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        """Run all rules over ``df`` sequentially."""
        for rule in self.rules:
            df = rule.apply(df)
        return df
