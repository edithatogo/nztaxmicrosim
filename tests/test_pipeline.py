"""Tests for the modular simulation pipeline."""

from dataclasses import dataclass

from src.pipeline import (
    IETCRule,
    IncomeTaxRule,
    SimulationPipeline,
)
from src.tax_calculator import TaxCalculator


@dataclass
class DummyRule:
    """A simple rule used for replacement tests."""

    name: str = "dummy"
    enabled: bool = True

    def apply(self, state: dict) -> None:  # pragma: no cover - trivial
        state["dummy"] = 1


def test_pipeline_runs_rules():
    calc = TaxCalculator.from_year("2024-2025")
    pipeline = SimulationPipeline([IncomeTaxRule(calc), IETCRule(calc)])
    state = {
        "taxable_income": 50_000,
        "is_wff_recipient": False,
        "is_super_recipient": False,
        "is_benefit_recipient": False,
    }
    result = pipeline.run(state)
    assert "income_tax" in result and result["income_tax"] > 0
    assert "ietc" in result and result["ietc"] >= 0


def test_enable_disable_rules():
    calc = TaxCalculator.from_year("2024-2025")
    pipeline = SimulationPipeline([IncomeTaxRule(calc), IETCRule(calc)])
    pipeline.disable("ietc")
    state = {"taxable_income": 30_000}
    result = pipeline.run(state)
    assert "ietc" not in result
    pipeline.enable("ietc")
    result = pipeline.run(state)
    assert "ietc" in result


def test_replace_rule():
    calc = TaxCalculator.from_year("2024-2025")
    pipeline = SimulationPipeline([IncomeTaxRule(calc)])
    pipeline.replace("income_tax", DummyRule())
    state = {"taxable_income": 10_000}
    result = pipeline.run(state)
    assert result["dummy"] == 1
    assert "income_tax" not in result
