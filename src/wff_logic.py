import numpy as np
import pandas as pd

from .parameters import WFFParams


def gross_up_income(df: pd.DataFrame, wagegwt: float) -> pd.DataFrame:
    """
    Gross up family income by a wage growth factor.

    This is done to project the family's income from the survey year to the
    simulation year.

    Args:
        df: DataFrame with a `familyinc` column.
        wagegwt: The wage growth rate to apply.

    Returns:
        A new DataFrame with an added `familyinc_grossed_up` column.
    """
    df = df.copy()
    df["familyinc_grossed_up"] = df["familyinc"] * (1 + wagegwt)
    return df


def calculate_abatement(df: pd.DataFrame, wff_params: WFFParams, daysinperiod: int) -> pd.DataFrame:
    """
    Calculate the abatement amounts for Working for Families (WFF) tax credits.

    WFF tax credits are abated (reduced) based on the family's income. There
    are two abatement thresholds and rates. The Best Start Tax Credit (BSTC)
    has its own separate abatement calculation.

    Args:
        df: DataFrame containing grossed up income and kid day counts.
        wff_params: The WFF parameters for the simulation year.
        daysinperiod: The number of days in the simulation period.

    Returns:
        A new DataFrame with `abate_amt` and `BSTCabate_amt` columns.
    """
    df = df.copy()
    df["abate_amt"] = np.where(
        df["familyinc_grossed_up"] <= wff_params.abatethresh1,
        0,
        np.where(
            df["familyinc_grossed_up"] <= wff_params.abatethresh2,
            (df["familyinc_grossed_up"] - wff_params.abatethresh1)
            * wff_params.abaterate1
            * df["maxkiddays"]
            / daysinperiod,
            (
                (wff_params.abatethresh2 - wff_params.abatethresh1) * wff_params.abaterate1
                + (df["familyinc_grossed_up"] - wff_params.abatethresh2) * wff_params.abaterate2
            )
            * df["maxkiddays"]
            / daysinperiod,
        ),
    )
    df["BSTCabate_amt"] = np.where(
        df["familyinc_grossed_up"] <= wff_params.bstcthresh,
        0,
        (df["familyinc_grossed_up"] - wff_params.bstcthresh)
        * wff_params.bstcabate
        * df["maxkiddaysbstc"]
        / daysinperiod,
    )
    return df


def calculate_max_entitlements(df: pd.DataFrame, wff_params: WFFParams) -> pd.DataFrame:
    """
    Calculate the maximum WFF entitlements before abatement.

    This function calculates the maximum possible entitlement for each of the
    Working for Families (WFF) tax credits:

    - Family Tax Credit (FTC)
    - In-Work Tax Credit (IWTC)
    - Best Start Tax Credit (BSTC)
    - Minimum Family Tax Credit (MFTC)

    The actual entitlement may be lower due to income abatement.

    Args:
        df: DataFrame with WFF weight and eligibility columns.
        wff_params: The WFF parameters for the simulation year.

    Returns:
        A new DataFrame with columns for the maximum entitlement for each
        WFF component.
    """
    df = df.copy()
    df["maxFTCent"] = np.where(
        df["FTCwgt"] <= 1,
        wff_params.ftc1 * df["FTCwgt"],
        wff_params.ftc1 + (df["FTCwgt"] - 1) * wff_params.ftc2,
    )

    df["maxIWTCent"] = np.where(
        df["IWTCwgt"] == 0,
        0,
        np.where(
            df["IWTCwgt"] <= 1,
            wff_params.iwtc1 * df["IWTCwgt"] * df["iwtc_elig"] / (12 * df["IWTCwgt"]),
            np.where(
                df["IWTCwgt"] <= 3,
                wff_params.iwtc1 * df["iwtc_elig"] / 12,
                (wff_params.iwtc1 + (df["IWTCwgt"] - 3) * wff_params.iwtc2) * df["iwtc_elig"] / 12,
            ),
        ),
    )

    df["maxBSTC0ent"] = np.minimum(np.maximum(df["BSTC0wgt"] - df["pplcnt"] / 26, 0), 1) * wff_params.bstc
    df["maxBSTC01ent"] = np.where(
        df["BSTC0wgt"] > 0,
        df["BSTC01wgt"] * wff_params.bstc,
        np.minimum(np.maximum(df["BSTC01wgt"] - df["pplcnt"] / 26, 0), 1) * wff_params.bstc,
    )
    df["maxBSTC1ent"] = wff_params.bstc * df["BSTC1wgt"]

    df["maxMFTCent"] = np.where(
        (df["familyinc_grossed_up"] < wff_params.mftc) & (df["MFTC_total"] > 0) & (df["MFTC_elig"] > 0),
        np.minimum((wff_params.mftc - df["familyinc_grossed_up"]) * (1 - 0.175), df["MFTC_total"]),
        0,
    )
    return df


def apply_care_logic(df: pd.DataFrame, wff_params: WFFParams) -> pd.DataFrame:
    """
    Apply shared and unshared care logic to compute WFF entitlements.

    The amount of Working for Families (WFF) tax credits a family receives
    can depend on whether the care of children is shared between parents.

    This function calculates the final entitlement for each WFF component
    after considering the care arrangements.

    Args:
        df: DataFrame containing maximum entitlement and abatement columns.
        wff_params: The WFF parameters for the simulation year.

    Returns:
        A new DataFrame with the final calculated FTC, IWTC, BSTC and MFTC
        amounts.
    """
    df = df.copy()
    df["FTCcalc"] = 0.0
    df["IWTCcalc"] = 0.0
    df["MFTCcalc"] = 0.0
    df["BSTCcalc"] = 0.0
    df["FTCcalcTEMP"] = 0.0
    df["carryforward_abate"] = 0.0

    # Unshared care
    unshared_care_mask = df["sharedcare"] == 0
    df.loc[unshared_care_mask, "FTCcalc"] = np.maximum(
        0, df.loc[unshared_care_mask, "maxFTCent"] - df.loc[unshared_care_mask, "abate_amt"]
    )
    df.loc[unshared_care_mask, "carryforward_abate"] = df.loc[unshared_care_mask, "abate_amt"] - (
        df.loc[unshared_care_mask, "maxFTCent"] - df.loc[unshared_care_mask, "FTCcalc"]
    )
    df.loc[unshared_care_mask, "IWTCcalc"] = np.maximum(
        0, df.loc[unshared_care_mask, "maxIWTCent"] - df.loc[unshared_care_mask, "carryforward_abate"]
    )
    df.loc[unshared_care_mask, "BSTCcalc"] = (
        df.loc[unshared_care_mask, "maxBSTC0ent"]
        + df.loc[unshared_care_mask, "maxBSTC01ent"]
        + np.maximum(0, df.loc[unshared_care_mask, "maxBSTC1ent"] - df.loc[unshared_care_mask, "BSTCabate_amt"])
    )
    df.loc[unshared_care_mask, "MFTCcalc"] = df.loc[unshared_care_mask, "maxMFTCent"]

    # Shared care
    shared_care_mask = df["sharedcare"] > 0
    df.loc[shared_care_mask, "FTCcalcTEMP"] = np.maximum(
        0, df.loc[shared_care_mask, "maxFTCent"] - df.loc[shared_care_mask, "abate_amt"]
    )
    df.loc[shared_care_mask, "FTCcalc"] = (
        df.loc[shared_care_mask, "FTCcalcTEMP"]
        * df.loc[shared_care_mask, "sharecareFTCwgt"]
        / df.loc[shared_care_mask, "FTCwgt"]
    )
    df.loc[shared_care_mask, "carryforward_abate"] = df.loc[shared_care_mask, "abate_amt"] - (
        df.loc[shared_care_mask, "maxFTCent"] - df.loc[shared_care_mask, "FTCcalcTEMP"]
    )
    df.loc[shared_care_mask, "IWTCcalc"] = np.maximum(
        0, df.loc[shared_care_mask, "maxIWTCent"] - df.loc[shared_care_mask, "carryforward_abate"]
    )

    bstccalc_shared: pd.Series[float] = pd.Series(0.0, index=df.index)
    bstc0_mask = (df["BSTC0wgt"] > 0) & shared_care_mask
    bstccalc_shared[bstc0_mask] += (
        df.loc[bstc0_mask, "maxBSTC0ent"] * df.loc[bstc0_mask, "sharecareBSTC0wgt"] / df.loc[bstc0_mask, "BSTC0wgt"]
    )

    bstc01_mask = (df["BSTC01wgt"] > 0) & shared_care_mask
    bstccalc_shared[bstc01_mask] += (
        df.loc[bstc01_mask, "maxBSTC01ent"]
        * df.loc[bstc01_mask, "sharecareBSTC01wgt"]
        / df.loc[bstc01_mask, "BSTC01wgt"]
    )

    bstc1_mask = (df["BSTC1wgt"] > 0) & shared_care_mask
    bstccalc_shared[bstc1_mask] += (
        np.maximum(0, wff_params.bstc - df.loc[bstc1_mask, "BSTCabate_amt"])
        * df.loc[bstc1_mask, "BSTC1wgt"]
        * df.loc[bstc1_mask, "sharecareBSTC1wgt"]
        / df.loc[bstc1_mask, "BSTC1wgt"]
    )

    df.loc[shared_care_mask, "BSTCcalc"] = bstccalc_shared[shared_care_mask]
    df.loc[shared_care_mask, "MFTCcalc"] = df.loc[shared_care_mask, "maxMFTCent"] * df.loc[shared_care_mask, "MFTCwgt"]
    return df


def apply_calibrations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply model calibrations to calculated WFF entitlements.

    This function makes adjustments to the calculated entitlements to better
    match real-world data.

    Currently, this function sets the In-Work Tax Credit (IWTC) to zero for
    self-employed individuals who are not otherwise entitled to it. This is
    because the model's rules may not perfectly capture the eligibility
    criteria for this group.

    Args:
        df: DataFrame with calculated entitlements.

    Returns:
        A new DataFrame with the calibrations applied.
    """
    df = df.copy()
    df.loc[(df["iwtc"] == 0) & (df["selfempind"] == 1), "IWTCcalc"] = 0
    return df
