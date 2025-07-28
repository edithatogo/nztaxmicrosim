import numpy as np
import pandas as pd


def famsim(
    df: pd.DataFrame,
    wff_params: dict[str, float],
    wagegwt: float,
    daysinperiod: int,
) -> pd.DataFrame:
    """
    Calculates the Working for Families (WFF) tax credits for a given dataset of families.

    This function replicates the logic of the SAS macro `%famsim` and applies a series
    of calculations to determine the entitlement for various WFF components, including
    Family Tax Credit (FTC), In-Work Tax Credit (IWTC), Best Start Tax Credit (BSTC),
    and Minimum Family Tax Credit (MFTC).

    The function takes a pandas DataFrame as input, where each row represents a family
    and contains all the necessary information for the calculation. It returns the same
    DataFrame with additional columns containing the calculated entitlements.

    Args:
        df (pd.DataFrame): A DataFrame containing family information.
        wff_params (dict): A dictionary of WFF parameters (ftc1, ftc2, iwtc1, iwtc2,
            bstc, mftc, abatethresh1, abatethresh2, abaterate1, abaterate2,
            bstcthresh, bstcabate).
        wagegwt (float): Wage growth - growth in average ordinary weekly earnings on a March year basis.
        daysinperiod (int): Number of days in the period.

    Returns:
        pd.DataFrame: The input DataFrame with additional columns for the calculated
            WFF entitlements.
    """
    # Gross up family income by wage growth
    df["familyinc_grossed_up"] = df["familyinc"] * (1 + wagegwt)

    # Abatement calculation
    df["abate_amt"] = np.where(
        df["familyinc_grossed_up"] <= wff_params["abatethresh1"],
        0,
        np.where(
            df["familyinc_grossed_up"] <= wff_params["abatethresh2"],
            (df["familyinc_grossed_up"] - wff_params["abatethresh1"])
            * wff_params["abaterate1"]
            * df["maxkiddays"]
            / daysinperiod,
            (
                (wff_params["abatethresh2"] - wff_params["abatethresh1"]) * wff_params["abaterate1"]
                + (df["familyinc_grossed_up"] - wff_params["abatethresh2"]) * wff_params["abaterate2"]
            )
            * df["maxkiddays"]
            / daysinperiod,
        ),
    )
    df["BSTCabate_amt"] = np.where(
        df["familyinc_grossed_up"] <= wff_params["bstcthresh"],
        0,
        (df["familyinc_grossed_up"] - wff_params["bstcthresh"])
        * wff_params["bstcabate"]
        * df["maxkiddaysbstc"]
        / daysinperiod,
    )

    # Maximum entitlement calculation
    df["maxFTCent"] = np.where(
        df["FTCwgt"] <= 1,
        wff_params["ftc1"] * df["FTCwgt"],
        wff_params["ftc1"] + (df["FTCwgt"] - 1) * wff_params["ftc2"],
    )

    df["maxIWTCent"] = np.where(
        df["IWTCwgt"] == 0,
        0,
        np.where(
            df["IWTCwgt"] <= 1,
            wff_params["iwtc1"] * df["IWTCwgt"] * df["iwtc_elig"] / (12 * df["IWTCwgt"]),
            np.where(
                df["IWTCwgt"] <= 3,
                wff_params["iwtc1"] * df["iwtc_elig"] / 12,
                (wff_params["iwtc1"] + (df["IWTCwgt"] - 3) * wff_params["iwtc2"]) * df["iwtc_elig"] / 12,
            ),
        ),
    )

    df["maxBSTC0ent"] = np.minimum(np.maximum(df["BSTC0wgt"] - df["pplcnt"] / 26, 0), 1) * wff_params["bstc"]
    df["maxBSTC01ent"] = np.where(
        df["BSTC0wgt"] > 0,
        df["BSTC01wgt"] * wff_params["bstc"],
        np.minimum(np.maximum(df["BSTC01wgt"] - df["pplcnt"] / 26, 0), 1) * wff_params["bstc"],
    )
    df["maxBSTC1ent"] = wff_params["bstc"] * df["BSTC1wgt"]

    df["maxMFTCent"] = np.where(
        (df["familyinc_grossed_up"] < wff_params["mftc"]) & (df["MFTC_total"] > 0) & (df["MFTC_elig"] > 0),
        np.minimum((wff_params["mftc"] - df["familyinc_grossed_up"]) * (1 - 0.175), df["MFTC_total"]),
        0,
    )

    # Abated entitlement calculation
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
        np.maximum(0, wff_params["bstc"] - df.loc[bstc1_mask, "BSTCabate_amt"])
        * df.loc[bstc1_mask, "BSTC1wgt"]
        * df.loc[bstc1_mask, "sharecareBSTC1wgt"]
        / df.loc[bstc1_mask, "BSTC1wgt"]
    )

    df.loc[shared_care_mask, "BSTCcalc"] = bstccalc_shared[shared_care_mask]

    df.loc[shared_care_mask, "MFTCcalc"] = df.loc[shared_care_mask, "maxMFTCent"] * df.loc[shared_care_mask, "MFTCwgt"]

    # Calibrations
    df.loc[(df["iwtc"] == 0) & (df["selfempind"] == 1), "IWTCcalc"] = 0

    return df
