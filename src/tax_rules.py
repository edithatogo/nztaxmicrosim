"""Rules for tax calculations."""

from dataclasses import dataclass
from typing import Any

from .acc_levy import calculate_acc_levy
from .parameters import ACCLevyParams
from .pipeline import Rule


@dataclass
class ACCLevyRule(Rule):
    """Rule to calculate ACC levy."""

    acc_levy_params: ACCLevyParams
    name: str = "acc_levy"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculates the ACC levy and adds it to the DataFrame."""
        df = data["df"]
        df["acc_levy"] = df["familyinc"].apply(
            lambda income: calculate_acc_levy(
                income=income,
                levy_rate=self.acc_levy_params.rate,
                max_income=self.acc_levy_params.max_income,
            )
        )
