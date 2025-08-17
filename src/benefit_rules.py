from dataclasses import dataclass
from typing import Any

from .benefits import (
    calculate_accommodation_supplement,
    calculate_bstc,
    calculate_disability_allowance,
    calculate_ftc,
    calculate_iwtc,
    calculate_jss,
    calculate_mftc,
    calculate_slp,
    calculate_sps,
    calculate_wep,
)
from .parameters import (
    AccommodationSupplementParams,
    BSTCParams,
    DisabilityAllowanceParams,
    FTCParams,
    IWTCParams,
    JSSParams,
    MFTCParams,
    SLPParams,
    SPSParams,
    WEPParams,
)
from .rule_registry import Rule, register_rule


@register_rule
@dataclass
class JSSRule(Rule):
    """A rule to calculate Jobseeker Support (JSS).

    JSS is a weekly payment for people who are not in full-time employment,
    are available for and looking for work, or are unable to work due to a
    health condition, injury, or disability.

    This rule calculates the JSS entitlement based on an individual's income,
    marital status, and number of dependent children.

    The calculation is performed by the `calculate_jss` function.
    """

    name: str = "JSSRule"
    enabled: bool = True
    jss_params: JSSParams | None = None

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculate JSS entitlement and add it to the DataFrame."""
        jss_params = data["params"].jss
        if not jss_params:
            return
        data["df"]["jss_entitlement"] = data["df"].apply(
            lambda row: calculate_jss(
                individual_income=row["total_individual_income_weekly"],
                is_single=row["marital_status"] == "Single",
                is_partnered=row["marital_status"] == "Married",
                num_dependent_children=row["num_children"],
                jss_params=jss_params,
            ),
            axis=1,
        )


@register_rule
@dataclass
class DisabilityAllowanceRule(Rule):
    """A rule to calculate the Disability Allowance.

    The Disability Allowance is a weekly payment for people who have regular,
    ongoing costs because of a disability.

    This rule calculates the Disability Allowance entitlement based on income,
    disability-related costs, and family situation.

    The calculation is performed by the `calculate_disability_allowance`
    function.
    """

    name: str = "DisabilityAllowanceRule"
    enabled: bool = True
    disability_allowance_params: DisabilityAllowanceParams | None = None

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculate Disability Allowance entitlement and add it to the DataFrame."""
        disability_allowance_params = data["params"].disability_allowance
        if not disability_allowance_params:
            return
        data["df"]["disability_allowance_entitlement"] = data["df"].apply(
            lambda row: calculate_disability_allowance(
                weekly_income=row["total_individual_income_weekly"],
                disability_costs=row.get("disability_costs", 0),
                family_situation=row["family_household_type"],
                params=disability_allowance_params,
            ),
            axis=1,
        )


@dataclass
class MFTCRule(Rule):
    """A rule to calculate the Minimum Family Tax Credit (MFTC).

    The MFTC is a payment for working families who would otherwise be better
    off on a benefit. It tops up their after-tax income to a guaranteed
    minimum amount.

    This rule calculates the MFTC entitlement based on family income and tax
    paid.

    The calculation is performed by the `calculate_mftc` function.
    """

    name: str = "MFTCRule"
    enabled: bool = True
    mftc_params: MFTCParams | None = None

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculate MFTC entitlement and add it to the DataFrame."""
        mftc_params = data["params"].mftc
        if not mftc_params:
            return
        df = data["df"]
        df["mftc_entitlement"] = df.apply(
            lambda row: calculate_mftc(
                family_income=row["familyinc"],
                tax_paid=row["tax_liability"],
                mftc_params=mftc_params,
            ),
            axis=1,
        )


@register_rule
@dataclass
class IWTCRule(Rule):
    """A rule to calculate the In-Work Tax Credit (IWTC).

    The IWTC is a payment for working families with dependent children. It is
    designed to help make work pay for low to middle-income families.

    This rule calculates the IWTC entitlement based on family income, number
    of children, and hours worked.

    The calculation is performed by the `calculate_iwtc` function.
    """

    name: str = "IWTCRule"
    enabled: bool = True
    iwtc_params: IWTCParams | None = None

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculate IWTC entitlement and add it to the DataFrame."""
        iwtc_params = data["params"].iwtc
        if not iwtc_params:
            return
        df = data["df"]
        df["iwtc_entitlement"] = df.apply(
            lambda row: calculate_iwtc(
                family_income=row["familyinc"],
                num_children=row["num_children"],
                hours_worked=row["hours_worked"],
                iwtc_params=iwtc_params,
            ),
            axis=1,
        )


@register_rule
@dataclass
class FTCRule(Rule):
    """A rule to calculate the Family Tax Credit (FTC).

    The FTC is a payment for families with dependent children. It is designed
    to help with the costs of raising a family.

    This rule calculates the FTC entitlement based on family income and the
    number of children.

    The calculation is performed by the `calculate_ftc` function.
    """

    name: str = "FTCRule"
    enabled: bool = True
    ftc_params: FTCParams | None = None

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculate FTC entitlement and add it to the DataFrame."""
        ftc_params = data["params"].ftc
        if not ftc_params:
            return
        df = data["df"]
        df["ftc_entitlement"] = df.apply(
            lambda row: calculate_ftc(
                family_income=row["familyinc"],
                num_children=row["num_children"],
                ftc_params=ftc_params,
            ),
            axis=1,
        )


@register_rule
@dataclass
class BSTCRule(Rule):
    """A rule to calculate the Best Start Tax Credit (BSTC).

    The BSTC is a payment for families with a new baby. It is designed to
    help with the costs of raising a child in their first few years.

    This rule calculates the BSTC entitlement based on family income and the
    age of the youngest child.

    The calculation is performed by the `calculate_bstc` function.
    """

    name: str = "BSTCRule"
    enabled: bool = True
    bstc_params: BSTCParams | None = None

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculate BSTC entitlement and add it to the DataFrame."""
        bstc_params = data["params"].bstc
        if not bstc_params:
            return
        df = data["df"]
        # Assume the first child's age is the relevant one for this calculation
        df["bstc_entitlement"] = df.apply(
            lambda row: calculate_bstc(
                family_income=row["familyinc"],
                child_age=row["ages_of_children"][0]
                if row.get("ages_of_children") and len(row["ages_of_children"]) > 0
                else 99,
                bstc_params=bstc_params,
            ),
            axis=1,
        )


@register_rule
@dataclass
class WEPRule(Rule):
    """A rule to calculate the Winter Energy Payment (WEP).

    The WEP is a payment to help with the cost of heating during the winter
    months. It is available to people receiving certain benefits or
    superannuation.

    This rule calculates the WEP entitlement based on eligibility, marital
    status, and number of dependent children.

    The calculation is performed by the `calculate_wep` function.
    """

    name: str = "WEPRule"
    enabled: bool = True
    wep_params: WEPParams | None = None

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculate WEP entitlement and add it to the DataFrame."""
        wep_params = data["params"].wep
        if not wep_params:
            return
        df = data["df"]
        df["wep_entitlement"] = df.apply(
            lambda row: calculate_wep(
                is_eligible=row.get("is_jss_recipient", False)
                or row.get("is_sps_recipient", False)
                or row.get("is_slp_recipient", False)
                or row.get("is_nz_super_recipient", False),
                is_single=row["marital_status"] == "Single",
                is_partnered=row["marital_status"] == "Married",
                num_dependent_children=row["num_children"],
                wep_params=wep_params,
            ),
            axis=1,
        )


@register_rule
@dataclass
class SPSRule(Rule):
    """A rule to calculate Sole Parent Support (SPS).

    SPS is a weekly payment for single parents with dependent children.

    This rule calculates the SPS entitlement based on an individual's income
    and the number of dependent children.

    The calculation is performed by the `calculate_sps` function.
    """

    name: str = "SPSRule"
    enabled: bool = True
    sps_params: SPSParams | None = None

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculate SPS entitlement and add it to the DataFrame."""
        sps_params = data["params"].sps
        if not sps_params:
            return
        data["df"]["sps_entitlement"] = data["df"].apply(
            lambda row: calculate_sps(
                individual_income=row["total_individual_income_weekly"],
                num_dependent_children=row["num_children"],
                sps_params=sps_params,
            ),
            axis=1,
        )


@register_rule
@dataclass
class SLPRule(Rule):
    """A rule to calculate Supported Living Payment (SLP).

    SLP is a weekly payment for people who have, or are caring for someone
    with, a significant health condition, injury, or disability.

    This rule calculates the SLP entitlement based on an individual's income,
    marital status, and disability status.

    The calculation is performed by the `calculate_slp` function.
    """

    name: str = "SLPRule"
    enabled: bool = True
    slp_params: SLPParams | None = None

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculate SLP entitlement and add it to the DataFrame."""
        slp_params = data["params"].slp
        if not slp_params:
            return
        data["df"]["slp_entitlement"] = data["df"].apply(
            lambda row: calculate_slp(
                individual_income=row["total_individual_income_weekly"],
                is_single=row["marital_status"] == "Single",
                is_partnered=row["marital_status"] == "Married",
                is_disabled=row["disability_status"],
                slp_params=slp_params,
            ),
            axis=1,
        )


@register_rule
@dataclass
class AccommodationSupplementRule(Rule):
    """A rule to calculate the Accommodation Supplement.

    The Accommodation Supplement is a weekly payment that helps people with
    their rent, board, or mortgage payments.

    This rule calculates the Accommodation Supplement entitlement based on
    household income, housing costs, region, and number of dependent children.

    The calculation is performed by the `calculate_accommodation_supplement`
    function.
    """

    name: str = "AccommodationSupplementRule"
    enabled: bool = True
    as_params: AccommodationSupplementParams | None = None

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculate Accommodation Supplement entitlement and add it to the DataFrame."""
        as_params = data["params"].accommodation_supplement
        if not as_params:
            return
        data["df"]["accommodation_supplement_entitlement"] = data["df"].apply(
            lambda row: calculate_accommodation_supplement(
                household_income=(row["total_individual_income_weekly"] * row["household_size"]),
                housing_costs=row["housing_costs"],
                region=row["region"],
                num_dependent_children=row["num_children"],
                as_params=as_params,
            ),
            axis=1,
        )
