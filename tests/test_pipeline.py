"""Tests for the modular simulation pipeline."""

from dataclasses import dataclass

from src.microsim import load_parameters
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
    value: int = 1
    enabled: bool = True

    def __call__(self, state: dict) -> None:  # pragma: no cover - trivial
        state[self.name] = self.value


import pandas as pd


def test_pipeline_integration_runs_rules():
    calc = TaxCalculator.from_year("2024-2025")
    pipeline = SimulationPipeline([IncomeTaxRule(calc), IETCRule(calc)])
    data = {
        "df": pd.DataFrame(
            {
                "familyinc": [50000],
                "is_wff_recipient": [False],
                "is_super_recipient": [False],
                "is_benefit_recipient": [False],
            }
        )
    }
    result = pipeline.run(data)
    assert "tax_liability" in result["df"].columns and result["df"]["tax_liability"][0] > 0
    assert "ietc" in result["df"].columns and result["df"]["ietc"][0] >= 0


def test_integration_enable_disable_rules():
    calc = TaxCalculator.from_year("2024-2025")
    pipeline = SimulationPipeline([IncomeTaxRule(calc), IETCRule(calc)])
    pipeline.disable("ietc")
    data = {"df": pd.DataFrame({"familyinc": [30000]})}
    result = pipeline.run(data)
    assert "ietc" not in result["df"].columns
    pipeline.enable("ietc")
    # Add the necessary columns for the ietc rule
    data["df"]["is_wff_recipient"] = False
    data["df"]["is_super_recipient"] = False
    data["df"]["is_benefit_recipient"] = False
    result = pipeline.run(data)
    assert "ietc" in result["df"].columns


def test_integration_replace_rule():
    calc = TaxCalculator.from_year("2024-2025")
    pipeline = SimulationPipeline([IncomeTaxRule(calc)])
    pipeline.replace("income_tax", DummyRule())
    data = {"df": pd.DataFrame({"familyinc": [10000]})}
    result = pipeline.run(data)
    assert result["dummy"] == 1
    assert "tax_liability" not in result["df"].columns


def test_pipeline_runs_rules() -> None:
    r1 = DummyRule("a", 1)
    r2 = DummyRule("b", 2)
    pipeline = SimulationPipeline([r1, r2])
    result = pipeline.run()
    assert result == {"a": 1, "b": 2}


def test_enable_disable_rules() -> None:
    r1 = DummyRule("a", 1)
    r2 = DummyRule("b", 2)
    pipeline = SimulationPipeline([r1, r2])
    pipeline.disable("b")
    assert pipeline.run() == {"a": 1}
    pipeline.enable("b")
    assert pipeline.run() == {"a": 1, "b": 2}


def test_replace_rule() -> None:
    r1 = DummyRule("a", 1)
    r2 = DummyRule("b", 2)
    pipeline = SimulationPipeline([r1, r2])
    pipeline.replace("b", DummyRule("b", 3))
    assert pipeline.run() == {"a": 1, "b": 3}


def test_pipeline_from_config(tmp_path):
    """Test creating a pipeline from a YAML configuration file."""
    config_content = """
    rules:
      - name: IncomeTaxRule
      - name: IETCRule
    """
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)

    params = load_parameters("2023-2024")
    pipeline = SimulationPipeline.from_config(str(config_file), params)

    assert len(pipeline.rules) == 2
    assert isinstance(pipeline.rules[0], IncomeTaxRule)
    assert isinstance(pipeline.rules[1], IETCRule)
