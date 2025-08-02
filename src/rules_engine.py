"""Lightweight rule engine for policy calculations.

This module defines a tiny framework that allows model calculations to be
expressed as a sequence of *rules*. Each rule encapsulates a single
transformation on a :class:`pandas.DataFrame`.  New policy steps can be added by
creating additional rules and appending them to the rule list used by a
`RuleEngine`.
"""

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping

import pandas as pd


@dataclass
class Rule:
    """A single transformation applied to a DataFrame."""

    name: str
    apply: Callable[[pd.DataFrame, Mapping[str, Any]], pd.DataFrame]


class RuleEngine:
    """Execute a sequence of rules against a DataFrame."""

    def __init__(self, rules: Iterable[Rule]):
        self.rules = list(rules)

    def run(self, df: pd.DataFrame, context: Mapping[str, Any]) -> pd.DataFrame:
        """Apply each rule in order and return the transformed DataFrame."""

        for rule in self.rules:
            df = rule.apply(df, context)
        return df
