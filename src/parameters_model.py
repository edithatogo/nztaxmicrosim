from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel, Field


class TaxBrackets(BaseModel):
    rates: List[float] = Field(..., description="Tax rates for each bracket.")
    thresholds: List[float] = Field(..., description="Income thresholds for tax brackets.")


class IETC(BaseModel):
    thrin: float
    ent: float
    thrab: float
    abrate: float


class WFF(BaseModel):
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


class JSS(BaseModel):
    single_rate: float
    couple_rate: float
    child_rate: float
    income_abatement_threshold: float
    abatement_rate: float


class SPS(BaseModel):
    base_rate: float
    income_abatement_threshold: float
    abatement_rate: float


class SLP(BaseModel):
    single_rate: float
    couple_rate: float
    income_abatement_threshold: float
    abatement_rate: float


class AccommodationSupplement(BaseModel):
    income_thresholds: Dict[str, float]
    abatement_rate: float
    max_entitlement_rates: Dict[str, Dict[str, float]]
    housing_cost_contribution_rate: float
    housing_cost_threshold: float


class TaxParameters(BaseModel):
    tax_brackets: TaxBrackets
    ietc: IETC = Field(..., alias="ietc")
    wff: WFF
    jss: JSS
    sps: SPS
    slp: SLP
    accommodation_supplement: AccommodationSupplement

    class Config:
        populate_by_name = True
        extra = "allow"
