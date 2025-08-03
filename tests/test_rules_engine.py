import pandas as pd

from src.rules_engine import Rule, RuleEngine


def test_rule_engine_applies_rules_in_order() -> None:
    df = pd.DataFrame({"a": [1, 2]})

    def add_one(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["a"] = df["a"] + 1
        return df

    engine = RuleEngine([Rule("add", add_one)])
    result = engine.run(df)
    assert list(result["a"]) == [2, 3]
