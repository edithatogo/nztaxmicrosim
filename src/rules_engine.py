from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List

import pandas as pd


@dataclass
class Rule:
    """
    A rule that represents a single transformation to be applied to a DataFrame.

    Each rule encapsulates a function (`func`) that performs the transformation,
    along with any options (`options`) that the function requires.

    Attributes:
        name: A human-readable name for the rule.
        func: The function that applies the transformation. It should accept a
            DataFrame as its first argument, and any other arguments as
            keywords.
        options: A dictionary of keyword arguments to be passed to `func`.
    """

    name: str
    func: Callable[..., pd.DataFrame]
    options: Dict[str, Any] = field(default_factory=dict)

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply the rule to a DataFrame.

        Args:
            df: The DataFrame to be transformed.

        Returns:
            The transformed DataFrame.
        """
        return self.func(df, **self.options)


class RuleEngine:
    """
    A class for executing a sequence of rules on a DataFrame.

    The RuleEngine stores a list of `Rule` objects and applies them
    sequentially to a DataFrame.
    """

    def __init__(self, rules: Iterable[Rule] | None = None) -> None:
        self.rules: List[Rule] = list(rules) if rules is not None else []

    def add_rule(self, rule: Rule) -> None:
        """
        Add a rule to the engine.

        Args:
            rule: The rule to be added.
        """
        self.rules.append(rule)

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Run all the rules in the engine on a DataFrame.

        The rules are applied sequentially in the order they were added.

        Args:
            df: The DataFrame to be processed.

        Returns:
            The processed DataFrame.
        """
        for rule in self.rules:
            df = rule.apply(df)
        return df