from dataclasses import dataclass
from typing import Any

from .benefits import (
    calculate_accommodation_supplement,
    calculate_jss,
    calculate_slp,
    calculate_sps,
)
from .parameters import (
    AccommodationSupplementParams,
    JSSParams,
    SLPParams,
    SPSParams,
)
from .pipeline import Rule


@dataclass
class JSSRule(Rule):
    """Rule to calculate Jobseeker Support."""

    jss_params: JSSParams
    name: str = "jss"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        data["df"]["jss_entitlement"] = data["df"].apply(
            lambda row: calculate_jss(
                individual_income=row["total_individual_income_weekly"],
                is_single=row["marital_status"] == "Single",
                is_partnered=row["marital_status"] == "Married",
                num_dependent_children=row["num_children"],
                jss_params=self.jss_params,
            ),
            axis=1,
        )


@dataclass
class MFTCRule(Rule):
    """Rule to calculate the Minimum Family Tax Credit."""

    mftc_params: "MFTCParams"
    name: str = "mftc"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculates the MFTC and adds it to the DataFrame."""
        from .benefits import calculate_mftc

        df = data["df"]
        df["mftc_entitlement"] = df.apply(
            lambda row: calculate_mftc(
                family_income=row["familyinc"],
                tax_paid=row["tax_liability"],
                mftc_params=self.mftc_params,
            ),
            axis=1,
        )


@dataclass
class IWTCRule(Rule):
    """Rule to calculate the In-Work Tax Credit."""

    iwtc_params: "IWTCParams"
    name: str = "iwtc"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculates the IWTC and adds it to the DataFrame."""
        from .benefits import calculate_iwtc

        df = data["df"]
        df["iwtc_entitlement"] = df.apply(
            lambda row: calculate_iwtc(
                family_income=row["familyinc"],
                num_children=row["num_children"],
                hours_worked=row["hours_worked"],
                iwtc_params=self.iwtc_params,
            ),
            axis=1,
        )


@dataclass
class FTCRule(Rule):
    """Rule to calculate the Family Tax Credit."""

    ftc_params: "FTCParams"
    name: str = "ftc"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculates the FTC and adds it to the DataFrame."""
        from .benefits import calculate_ftc

        df = data["df"]
        df["ftc_entitlement"] = df.apply(
            lambda row: calculate_ftc(
                family_income=row["familyinc"],
                num_children=row["num_children"],
                ftc_params=self.ftc_params,
            ),
            axis=1,
        )


@dataclass
class BSTCRule(Rule):
    """Rule to calculate the Best Start Tax Credit."""

    bstc_params: "BSTCParams"
    name: str = "bstc"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculates the BSTC and adds it to the DataFrame."""
        from .benefits import calculate_bstc

        df = data["df"]
        # Assume the first child's age is the relevant one for this calculation
        df["bstc_entitlement"] = df.apply(
            lambda row: calculate_bstc(
                family_income=row["familyinc"],
                child_age=row["ages_of_children"][0] if row["ages_of_children"] else 99,
                bstc_params=self.bstc_params,
            ),
            axis=1,
        )


try:
    from .parameters import WEPParams
except ImportError:
    WEPParams = None

@dataclass
class WEPRule(Rule):
    """Rule to calculate the Winter Energy Payment."""

    wep_params: "WEPParams"
    name: str = "wep"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculates the WEP and adds it to the DataFrame."""
        if not self.wep_params:
            return
        from .benefits import calculate_wep

        df = data["df"]
        df["wep_entitlement"] = df.apply(
            lambda row: calculate_wep(
                is_eligible=row["is_jss_recipient"]
                or row["is_sps_recipient"]
                or row["is_slp_recipient"]
                or row["is_nz_super_recipient"],
                is_single=row["marital_status"] == "Single",
                is_partnered=row["marital_status"] == "Married",
                num_dependent_children=row["num_children"],
                wep_params=self.wep_params,
            ),
            axis=1,
        )


@dataclass
class SPSRule(Rule):
    """Rule to calculate Sole Parent Support."""

    sps_params: SPSParams
    name: str = "sps"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        data["df"]["sps_entitlement"] = data["df"].apply(
            lambda row: calculate_sps(
                individual_income=row["total_individual_income_weekly"],
                num_dependent_children=row["num_children"],
                sps_params=self.sps_params,
            ),
            axis=1,
        )


@dataclass
class SLPRule(Rule):
    """Rule to calculate Supported Living Payment."""

    slp_params: SLPParams
    name: str = "slp"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        data["df"]["slp_entitlement"] = data["df"].apply(
            lambda row: calculate_slp(
                individual_income=row["total_individual_income_weekly"],
                is_single=row["marital_status"] == "Single",
                is_partnered=row["marital_status"] == "Married",
                is_disabled=row["disability_status"],
                slp_params=self.slp_params,
            ),
            axis=1,
        )


@dataclass
class AccommodationSupplementRule(Rule):
    """Rule to calculate Accommodation Supplement."""

    as_params: AccommodationSupplementParams
    name: str = "accommodation_supplement"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        data["df"]["accommodation_supplement_entitlement"] = data["df"].apply(
            lambda row: calculate_accommodation_supplement(
                household_income=(row["total_individual_income_weekly"] * row["household_size"]),
                housing_costs=row["housing_costs"],
                region=row["region"],
                num_dependent_children=row["num_children"],
                as_params=self.as_params,
            ),
            axis=1,
        )
