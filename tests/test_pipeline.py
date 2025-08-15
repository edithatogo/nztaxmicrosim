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
    config_content = """
    rules:
      - name: JSSRule
      - name: IncomeTaxRule
      - name: KiwiSaverRule
        params:
          enabled: false
    """
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)

    params = load_parameters("2024-2025")
    pipeline = SimulationPipeline.from_config(str(config_file), params.model_dump())

    assert len(pipeline.rules) == 3
    assert pipeline.rules[0].__class__.__name__ == "JSSRule"
    assert pipeline.rules[1].__class__.__name__ == "IncomeTaxRule"
    assert pipeline.rules[2].__class__.__name__ == "KiwiSaverRule"
    assert not pipeline.rules[2].enabled


def test_pipeline_from_config_unknown_rule(tmp_path):
    """Test that creating a pipeline from a YAML file with an unknown rule raises an error."""
    config_content = """
    rules:
      - name: UnknownRule
    """
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)

    params = load_parameters("2023-2024")
    with pytest.raises(ValueError, match="Unknown rule: UnknownRule"):
        SimulationPipeline.from_config(str(config_file), params.model_dump())
