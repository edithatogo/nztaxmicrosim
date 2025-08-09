from __future__ import annotations

from pydantic import BaseModel, Field


class TaxBracketParams(BaseModel):
    rates: list[float]
    thresholds: list[float]


class IETCParams(BaseModel):
    thrin: float
    ent: float
    thrab: float
    abrate: float


class WFFParams(BaseModel):
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


class JSSParams(BaseModel):
    single_rate: float
    couple_rate: float
    child_rate: float
    income_abatement_threshold: float
    abatement_rate: float


class SPSParams(BaseModel):
    base_rate: float
    income_abatement_threshold: float
    abatement_rate: float


class SLPParams(BaseModel):
    single_rate: float
    couple_rate: float
    income_abatement_threshold: float
    abatement_rate: float


class AccommodationSupplementParams(BaseModel):
    income_thresholds: dict[str, float]
    abatement_rate: float
    max_entitlement_rates: dict[str, dict[str, float]]
    housing_cost_contribution_rate: float
    housing_cost_threshold: float


class FamilyBoostParams(BaseModel):
    max_credit: float = 0.0
    income_threshold: float = 0.0
    abatement_rate: float = 0.0
    max_income: float = 0.0


class PPLParams(BaseModel):
    enabled: bool = False
    weekly_rate: float = 0.0
    max_weeks: int = 0


class ChildSupportParams(BaseModel):
    enabled: bool = False
    support_rate: float = 0.0


class KiwisaverParams(BaseModel):
    contribution_rate: float = 0.0


class RWTParams(BaseModel):
    rwt_rate_10_5: float = 0.0
    rwt_rate_17_5: float = 0.0
    rwt_rate_30: float = 0.0
    rwt_rate_33: float = 0.0
    rwt_rate_39: float = 0.0


class StudentLoanParams(BaseModel):
    repayment_threshold: float = 0.0
    repayment_rate: float = 0.0


<<<<<<< HEAD
class Parameters(BaseModel):
    tax_brackets: TaxBracketParams
    ietc: IETCParams
    wff: WFFParams
    jss: JSSParams
    sps: SPSParams
    slp: SLPParams
    accommodation_supplement: AccommodationSupplementParams
    family_boost: FamilyBoostParams = Field(default_factory=FamilyBoostParams)
    ppl: PPLParams = Field(default_factory=PPLParams)
    child_support: ChildSupportParams = Field(default_factory=ChildSupportParams)
    kiwisaver: KiwisaverParams = Field(default_factory=KiwisaverParams)
    student_loan: StudentLoanParams = Field(default_factory=StudentLoanParams)
    rwt: RWTParams = Field(default_factory=RWTParams)


__all__ = [
    "AccommodationSupplementParams",
    "ChildSupportParams",
    "FamilyBoostParams",
    "IETCParams",
    "JSSParams",
    "KiwisaverParams",
    "Parameters",
    "PPLParams",
    "RWTParams",
    "SLPParams",
    "SPSParams",
    "StudentLoanParams",
    "TaxBracketParams",
    "WFFParams",
]
