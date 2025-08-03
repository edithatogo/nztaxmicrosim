from dataclasses import dataclass

from src.pipeline import SimulationPipeline


@dataclass
class DummyRule:
    name: str
    value: int
    enabled: bool = True

    def __call__(self, data: dict) -> None:
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
