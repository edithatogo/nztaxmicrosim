from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, List

import pandas as pd


@dataclass
class Rule:
    """A single transformation applied to a :class:`pandas.DataFrame`."""

    func: Callable[[pd.DataFrame], pd.DataFrame]

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.func(df)


class RuleEngine:
    """Execute a sequence of :class:`Rule` objects."""

    def __init__(self, rules: Iterable[Rule] | None = None) -> None:
        self.rules: List[Rule] = list(rules) if rules is not None else []

    def add_rule(self, rule: Rule) -> None:
        self.rules.append(rule)

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        for rule in self.rules:
            df = rule.apply(df)
        return df
