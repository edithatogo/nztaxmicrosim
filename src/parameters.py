from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from typing import Any, Dict, List


def _require_fields(data: Dict[str, Any], required: List[str]) -> None:
    """Ensure all required fields are present in ``data``."""
    missing = [field for field in required if field not in data]
    if missing:
        raise KeyError(f"Missing required fields: {', '.join(missing)}")


@dataclass
class TaxBracketParams:
    rates: List[float]
    thresholds: List[float]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaxBracketParams":
        _require_fields(data, ["rates", "thresholds"])
        if not isinstance(data["rates"], list) or not isinstance(data["thresholds"], list):
            raise TypeError("rates and thresholds must be lists")
        return cls(
            rates=[float(r) for r in data["rates"]],
            thresholds=[float(t) for t in data["thresholds"]],
        )


@dataclass
class IETCParams:
    thrin: float
    ent: float
    thrab: float
    abrate: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IETCParams":
        required = ["thrin", "ent", "thrab", "abrate"]
        _require_fields(data, required)
        return cls(**{k: float(data[k]) for k in required})


@dataclass
class WFFParams:
    ftc1: float
    ftc2: float
    iwtc1: float
    iwtc2: float
    bstc: float
    mftc: float
    abatethresh1: float
    abatethresh2: float
    abaterate1: float
    abaterate2: float
    bstcthresh: float
    bstcabate: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WFFParams":
        required = [
            "ftc1",
            "ftc2",
            "iwtc1",
            "iwtc2",
            "bstc",
            "mftc",
            "abatethresh1",
            "abatethresh2",
            "abaterate1",
            "abaterate2",
            "bstcthresh",
            "bstcabate",
        ]
        _require_fields(data, required)
        return cls(**{k: float(data[k]) for k in required})


@dataclass
class JSSParams:
    single_rate: float
    couple_rate: float
    child_rate: float
    income_abatement_threshold: float
    abatement_rate: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JSSParams":
        required = [
            "single_rate",
            "couple_rate",
            "child_rate",
            "income_abatement_threshold",
            "abatement_rate",
        ]
        _require_fields(data, required)
        return cls(**{k: float(data[k]) for k in required})


@dataclass
class SPSParams:
    base_rate: float
    income_abatement_threshold: float
    abatement_rate: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SPSParams":
        required = ["base_rate", "income_abatement_threshold", "abatement_rate"]
        _require_fields(data, required)
        return cls(**{k: float(data[k]) for k in required})


@dataclass
class SLPParams:
    single_rate: float
    couple_rate: float
    income_abatement_threshold: float
    abatement_rate: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SLPParams":
        required = [
            "single_rate",
            "couple_rate",
            "income_abatement_threshold",
            "abatement_rate",
        ]
        _require_fields(data, required)
        return cls(**{k: float(data[k]) for k in required})


@dataclass
class AccommodationSupplementParams:
    income_thresholds: Dict[str, float]
    abatement_rate: float
    max_entitlement_rates: Dict[str, Dict[str, float]]
    housing_cost_contribution_rate: float
    housing_cost_threshold: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AccommodationSupplementParams":
        required = [
            "income_thresholds",
            "abatement_rate",
            "max_entitlement_rates",
            "housing_cost_contribution_rate",
            "housing_cost_threshold",
        ]
        _require_fields(data, required)
        if not isinstance(data["income_thresholds"], dict) or not isinstance(data["max_entitlement_rates"], dict):
            raise TypeError("income_thresholds and max_entitlement_rates must be dicts")
        income_thresholds = {k: float(v) for k, v in data["income_thresholds"].items()}
        max_entitlement_rates = {
            region: {k: float(v) for k, v in rates.items()} for region, rates in data["max_entitlement_rates"].items()
        }
        return cls(
            income_thresholds=income_thresholds,
            abatement_rate=float(data["abatement_rate"]),
            max_entitlement_rates=max_entitlement_rates,
            housing_cost_contribution_rate=float(data["housing_cost_contribution_rate"]),
            housing_cost_threshold=float(data["housing_cost_threshold"]),
        )


@dataclass
class FamilyBoostParams:
    max_credit: float
    income_threshold: float
    abatement_rate: float
    max_income: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FamilyBoostParams":
        required = ["max_credit", "income_threshold", "abatement_rate", "max_income"]
        _require_fields(data, required)
        return cls(**{k: float(data[k]) for k in required})


@dataclass
class PPLParams:
    enabled: bool
    weekly_rate: float
    max_weeks: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PPLParams":
        required = ["enabled", "weekly_rate", "max_weeks"]
        _require_fields(data, required)
        return cls(
            enabled=bool(data["enabled"]),
            weekly_rate=float(data["weekly_rate"]),
            max_weeks=int(data["max_weeks"]),
        )


@dataclass
class RWTParams:
    rwt_rate_10_5: float
    rwt_rate_17_5: float
    rwt_rate_30: float
    rwt_rate_33: float
    rwt_rate_39: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RWTParams":
        required = [
            "rwt_rate_10_5",
            "rwt_rate_17_5",
            "rwt_rate_30",
            "rwt_rate_33",
            "rwt_rate_39",
        ]
        _require_fields(data, required)
        return cls(**{k: float(data[k]) for k in required})


@dataclass
class ChildSupportParams:
    enabled: bool
    support_rate: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChildSupportParams":
        required = ["enabled", "support_rate"]
        _require_fields(data, required)
        return cls(enabled=bool(data["enabled"]), support_rate=float(data["support_rate"]))


@dataclass
class KiwisaverParams:
    contribution_rate: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KiwisaverParams":
        required = ["contribution_rate"]
        _require_fields(data, required)
        return cls(contribution_rate=float(data["contribution_rate"]))


@dataclass
class StudentLoanParams:
    repayment_threshold: float
    repayment_rate: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StudentLoanParams":
        required = ["repayment_threshold", "repayment_rate"]
        _require_fields(data, required)
        return cls(
            repayment_threshold=float(data["repayment_threshold"]),
            repayment_rate=float(data["repayment_rate"]),
        )


@dataclass
class Parameters:
    tax_brackets: TaxBracketParams
    ietc: IETCParams
    wff: WFFParams
    jss: JSSParams
    sps: SPSParams
    slp: SLPParams
    accommodation_supplement: AccommodationSupplementParams
    family_boost: FamilyBoostParams
    ppl: PPLParams
    rwt: RWTParams
    child_support: ChildSupportParams
    kiwisaver: KiwisaverParams
    student_loan: StudentLoanParams

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Parameters":
        return cls(
            tax_brackets=TaxBracketParams.from_dict(data["tax_brackets"]),
            ietc=IETCParams.from_dict(data["ietc"]),
            wff=WFFParams.from_dict(data["wff"]),
            jss=JSSParams.from_dict(data["jss"]),
            sps=SPSParams.from_dict(data["sps"]),
            slp=SLPParams.from_dict(data["slp"]),
            accommodation_supplement=AccommodationSupplementParams.from_dict(data["accommodation_supplement"]),
            family_boost=FamilyBoostParams.from_dict(
                data.get(
                    "family_boost",
                    {
                        "max_credit": 0.0,
                        "income_threshold": 0.0,
                        "abatement_rate": 0.0,
                        "max_income": 0.0,
                    },
                )
            ),
            ppl=PPLParams.from_dict(data.get("ppl", {"enabled": False, "weekly_rate": 0.0, "max_weeks": 0})),
            rwt=RWTParams.from_dict(
                data.get(
                    "rwt",
                    {
                        "rwt_rate_10_5": 0.0,
                        "rwt_rate_17_5": 0.0,
                        "rwt_rate_30": 0.0,
                        "rwt_rate_33": 0.0,
                        "rwt_rate_39": 0.0,
                    },
                )
            ),
            child_support=ChildSupportParams.from_dict(
                data.get("child_support", {"enabled": False, "support_rate": 0.0})
            ),
            kiwisaver=KiwisaverParams.from_dict(data.get("kiwisaver", {"contribution_rate": 0.0})),
            student_loan=StudentLoanParams.from_dict(
                data.get(
                    "student_loan",
                    {"repayment_threshold": 0.0, "repayment_rate": 0.0},
                )
            ),
        )

    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access to parameter groups.

        If the requested attribute is itself a dataclass it is converted to a
        plain ``dict`` for compatibility with code that expects mapping-style
        parameters. Nested dataclasses are converted to dictionaries to provide a
        serialization-friendly view of the parameters.
        """
        value = getattr(self, key)
        if is_dataclass(value):
            return asdict(value)
        return value