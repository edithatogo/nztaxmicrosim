"""Tests for the modular simulation pipeline."""

from dataclasses import dataclass
from typing import Any

import pytest

from src.microsim import load_parameters
from src.pipeline import SimulationPipeline


@dataclass
class DummyRule:
    """A simple rule used for replacement tests."""

    name: str = "dummy"
    value: int = 1
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        data[self.name] = self.value

    def apply(self, data: dict[str, Any]) -> None:  # pragma: no cover - trivial
        data[self.name] = self.value


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
    # This test now uses the real rule names.
    config_content = """
    rules:
      - name: JSSRule
      - name: IncomeTaxRule
      - name: KiwiSaverRule
    """
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)

    pipeline = SimulationPipeline.from_config(str(config_file))

    assert len(pipeline.rules) == 3
    assert pipeline.rules[0].__class__.__name__ == "JSSRule"
    assert pipeline.rules[1].__class__.__name__ == "IncomeTaxRule"
    assert pipeline.rules[2].__class__.__name__ == "KiwiSaverRule"

    # Test running the pipeline with the necessary context
    params = load_parameters("2024-2025")
    tax_calc = TaxCalculator(params=params)
    data = {
        "df": pd.DataFrame({
            "familyinc": [50000], "marital_status": ["Single"], "num_children": [0],
            "total_individual_income_weekly": [50000 / 52]
        }),
        "params": params,
        "tax_calc": tax_calc,
    }

    # We can't easily mock the __call__ methods now because they are part of a Protocol
    # so we'll just run the pipeline and check that it doesn't crash and produces output.
    result_data = pipeline.run(data)
    assert "jss_entitlement" in result_data["df"].columns
    assert "tax_liability" in result_data["df"].columns
    assert "kiwisaver_contribution" in result_data["df"].columns


def test_pipeline_from_config_unknown_rule(tmp_path):
    """Test that creating a pipeline from a YAML file with an unknown rule raises an error."""
    config_content = """
    rules:
      - name: UnknownRule
    """
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)

    with pytest.raises(ValueError, match="Unknown rule: UnknownRule"):
        SimulationPipeline.from_config(str(config_file))
