import pandas as pd

from src.rules_engine import Rule, RuleEngine


def test_rule_engine_applies_rules_in_order() -> None:
    df = pd.DataFrame({"a": [1, 2]})

    def add_one(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["a"] = df["a"] + 1
        return df

    def multiply_by_two(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["a"] = df["a"] * 2
        return df

    engine = RuleEngine([Rule("add", add_one), Rule("multiply", multiply_by_two)])
    result = engine.run(df)
    # Expected: (1 + 1) * 2 = 4, (2 + 1) * 2 = 6
    assert list(result["a"]) == [4, 6]
