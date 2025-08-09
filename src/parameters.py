from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class TaxBracketParams(BaseModel):
    """Parameters for the progressive income tax brackets."""

    rates: list[float]
    thresholds: list[float]


class IETCParams(BaseModel):
    """Parameters for the Independent Earner Tax Credit (IETC)."""

    thrin: float = Field(description="The income threshold above which IETC is available.")
    ent: float = Field(description="The maximum entitlement amount.")
    thrab: float = Field(description="The income threshold at which the abatement begins.")
    abrate: float = Field(description="The abatement rate for the credit.")


class WFFParams(BaseModel):
    """Parameters for the Working for Families (WFF) tax credits."""

    ftc1: float = Field(description="Family Tax Credit rate for the first child.")
    ftc2: float = Field(description="Family Tax Credit rate for subsequent children.")
    iwtc1: float = Field(description="In-Work Tax Credit rate for the first child.")
    iwtc2: float = Field(description="In-Work Tax Credit rate for subsequent children.")
    bstc: float = Field(description="Best Start Tax Credit rate.")
    mftc: float = Field(description="Minimum Family Tax Credit rate.")
    abatethresh1: float = Field(description="First abatement threshold for WFF credits.")
    abatethresh2: float = Field(description="Second abatement threshold for WFF credits.")
    abaterate1: float = Field(description="First abatement rate for WFF credits.")
    abaterate2: float = Field(description="Second abatement rate for WFF credits.")
    bstcthresh: float = Field(description="Best Start Tax Credit abatement threshold.")
    bstcabate: float = Field(description="Best Start Tax Credit abatement rate.")


class JSSParams(BaseModel):
    """Parameters for Jobseeker Support (JSS)."""

    single_rate: float = Field(description="The weekly benefit rate for a single person.")
    couple_rate: float = Field(description="The weekly benefit rate for a couple.")
    child_rate: float = Field(description="The additional weekly benefit rate per child.")
    income_abatement_threshold: float = Field(description="The income threshold at which the abatement begins.")
    abatement_rate: float = Field(description="The abatement rate for the benefit.")


class SPSParams(BaseModel):
    """Parameters for Sole Parent Support (SPS)."""

    base_rate: float = Field(description="The base weekly benefit rate.")
    income_abatement_threshold: float = Field(description="The income threshold at which the abatement begins.")
    abatement_rate: float = Field(description="The abatement rate for the benefit.")


class SLPParams(BaseModel):
    """Parameters for Supported Living Payment (SLP)."""

    single_rate: float = Field(description="The weekly benefit rate for a single person.")
    couple_rate: float = Field(description="The weekly benefit rate for a couple.")
    income_abatement_threshold: float = Field(description="The income threshold at which the abatement begins.")
    abatement_rate: float = Field(description="The abatement rate for the benefit.")


class AccommodationSupplementParams(BaseModel):
    """Parameters for the Accommodation Supplement."""

    income_thresholds: dict[str, float] = Field(description="Income thresholds by region.")
    abatement_rate: float = Field(description="The abatement rate for the supplement.")
    max_entitlement_rates: dict[str, dict[str, float]] = Field(
        description="Maximum entitlement rates by region and family type."
    )
    housing_cost_contribution_rate: float = Field(
        description="The rate at which housing costs are contributed to the calculation."
    )
    housing_cost_threshold: float = Field(description="The threshold for housing costs.")


class FamilyBoostParams(BaseModel):
    """Parameters for the FamilyBoost childcare tax credit."""

    max_credit: float = Field(default=0.0, description="The maximum credit amount.")
    income_threshold: float = Field(default=0.0, description="The income threshold at which the abatement begins.")
    abatement_rate: float = Field(default=0.0, description="The abatement rate for the credit.")
    max_income: float = Field(default=0.0, description="The maximum income at which the credit is available.")


class PPLParams(BaseModel):
    """Parameters for Paid Parental Leave (PPL)."""

    enabled: bool = Field(default=False, description="Whether PPL is enabled.")
    weekly_rate: float = Field(default=0.0, description="The weekly payment rate.")
    max_weeks: int = Field(default=0, description="The maximum number of weeks the payment is available.")


class ChildSupportParams(BaseModel):
    """Parameters for Child Support payments."""

    enabled: bool = Field(default=False, description="Whether Child Support is enabled.")
    support_rate: float = Field(default=0.0, description="The rate at which child support is calculated.")


class KiwisaverParams(BaseModel):
    """Parameters for KiwiSaver contributions."""

    contribution_rate: float = Field(default=0.0, description="The default employee contribution rate.")


class RWTParams(BaseModel):
    """Parameters for Resident Withholding Tax (RWT)."""

    rwt_rate_10_5: float = Field(default=0.0, description="The RWT rate for the 10.5% tax bracket.")
    rwt_rate_17_5: float = Field(default=0.0, description="The RWT rate for the 17.5% tax bracket.")
    rwt_rate_30: float = Field(default=0.0, description="The RWT rate for the 30% tax bracket.")
    rwt_rate_33: float = Field(default=0.0, description="The RWT rate for the 33% tax bracket.")
    rwt_rate_39: float = Field(default=0.0, description="The RWT rate for the 39% tax bracket.")


class ACCLevyParams(BaseModel):
    """Parameters for the ACC Earner's Levy."""

    rate: float = Field(description="The levy rate.")
    max_income: float = Field(description="The maximum income on which the levy is applied.")


class WEPParams(BaseModel):
    """Parameters for the Winter Energy Payment (WEP)."""

    single_rate: float = Field(description="The weekly payment rate for a single person.")
    couple_rate: float = Field(description="The weekly payment rate for a couple.")
    child_rate: float = Field(description="The additional weekly payment rate per child.")




class StudentLoanParams(BaseModel):
    """Parameters for Student Loan repayments."""

    repayment_threshold: float = Field(default=0.0, description="The annual income threshold for repayments.")
    repayment_rate: float = Field(default=0.0, description="The repayment rate.")


class BSTCParams(BaseModel):
    """Parameters for the Best Start Tax Credit (BSTC)."""

    threshold: float = Field(description="The income threshold at which the abatement begins.")
    rate: float = Field(description="The abatement rate for the credit.")
    amount: float = Field(description="The credit amount.")
    max_age: int = Field(description="The maximum age of a child for eligibility.")


class FTCParams(BaseModel):
    """Parameters for the Family Tax Credit (FTC)."""

    base_rate: float = Field(description="The base weekly credit rate.")
    child_rate: float = Field(description="The additional weekly credit rate per child.")
    income_threshold: float = Field(description="The income threshold at which the abatement begins.")
    abatement_rate: float = Field(description="The abatement rate for the credit.")


class IWTCParams(BaseModel):
    """Parameters for the In-Work Tax Credit (IWTC)."""

    base_rate: float = Field(description="The base weekly credit rate.")
    child_rate: float = Field(description="The additional weekly credit rate per child.")
    income_threshold: float = Field(description="The income threshold at which the abatement begins.")
    abatement_rate: float = Field(description="The abatement rate for the credit.")
    min_hours_worked: int = Field(description="The minimum hours worked to be eligible.")


class MFTCParams(BaseModel):
    """Parameters for the Minimum Family Tax Credit (MFTC)."""

    guaranteed_income: float = Field(description="The guaranteed minimum family income.")


class Parameters(BaseModel):
    """
    A container for all the parameters for a given tax year.

    The parameters are loaded from a JSON file corresponding to the year being
    simulated. For example, the parameters for the 2023-2024 tax year are
    loaded from `parameters_2023-2024.json`.

    This class is a Pydantic model, which means that the parameters are
    validated when they are loaded. This helps to ensure that the parameters
    are correct and complete.

    The parameters are grouped into the following categories:

    - `tax_brackets`: Parameters for the progressive income tax brackets.
    - `ietc`: Parameters for the Independent Earner Tax Credit (IETC).
    - `wff`: Parameters for the Working for Families (WFF) tax credits.
    - `jss`: Parameters for Jobseeker Support (JSS).
    - `sps`: Parameters for Sole Parent Support (SPS).
    - `slp`: Parameters for Supported Living Payment (SLP).
    - `accommodation_supplement`: Parameters for the Accommodation Supplement.
    - `bstc`: Parameters for the Best Start Tax Credit (BSTC).
    - `ftc`: Parameters for the Family Tax Credit (FTC).
    - `iwtc`: Parameters for the In-Work Tax Credit (IWTC).
    - `mftc`: Parameters for the Minimum Family Tax Credit (MFTC).
    - `family_boost`: Parameters for the FamilyBoost childcare tax credit.
    - `ppl`: Parameters for Paid Parental Leave (PPL).
    - `child_support`: Parameters for Child Support payments.
    - `kiwisaver`: Parameters for KiwiSaver contributions.
    - `student_loan`: Parameters for Student Loan repayments.
    - `rwt`: Parameters for Resident Withholding Tax (RWT).
    - `acc_levy`: Parameters for the ACC Earner's Levy.
    - `wep`: Parameters for the Winter Energy Payment (WEP).
    """

    tax_brackets: TaxBracketParams
    ietc: IETCParams
    wff: WFFParams
    jss: JSSParams
    sps: SPSParams
    slp: SLPParams
    accommodation_supplement: AccommodationSupplementParams
    bstc: Optional[BSTCParams] = None
    ftc: Optional[FTCParams] = None
    iwtc: Optional[IWTCParams] = None
    mftc: Optional[MFTCParams] = None
    family_boost: FamilyBoostParams = Field(default_factory=FamilyBoostParams)
    ppl: PPLParams = Field(default_factory=PPLParams)
    child_support: ChildSupportParams = Field(default_factory=ChildSupportParams)
    kiwisaver: KiwisaverParams = Field(default_factory=KiwisaverParams)
    student_loan: StudentLoanParams = Field(default_factory=StudentLoanParams)
    rwt: RWTParams = Field(default_factory=RWTParams)
    acc_levy: Optional[ACCLevyParams] = None
    wep: Optional[WEPParams] = None


__all__ = [
    "AccommodationSupplementParams",
    "ACCLevyParams",
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
    "WEPParams",
    "WFFParams",
]
