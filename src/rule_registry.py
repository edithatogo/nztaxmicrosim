"""Rule registry for the simulation pipeline."""

from __future__ import annotations

from typing import Any, Protocol, Type

RULE_REGISTRY: dict[str, Type[Rule]] = {}


def register_rule(cls: Type[Rule]) -> Type[Rule]:
    """A class decorator to register a rule in the RULE_REGISTRY."""
    RULE_REGISTRY[cls.__name__] = cls
    return cls


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
