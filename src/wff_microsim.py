import numpy as np
import pandas as pd

from .parameters import WFFParams
from .rules_engine import Rule, RuleEngine


def gross_up_income(df: pd.DataFrame, wagegwt: float) -> pd.DataFrame:
    """Gross up family income by wage growth.

    Args:
        df: DataFrame with a ``familyinc`` column.
        wagegwt: Wage growth rate.

    Returns:
        DataFrame with an added ``familyinc_grossed_up`` column.
    """
    df = df.copy()
    df["familyinc_grossed_up"] = df["familyinc"] * (1 + wagegwt)
    return df


def calculate_abatement(df: pd.DataFrame, wff_params: WFFParams, daysinperiod: int) -> pd.DataFrame:
    """Calculate WFF abatement amounts.

    Args:
        df: DataFrame containing grossed up income and kid day counts.
        wff_params: Working for Families parameters.
        daysinperiod: Number of days in the period.

    Returns:
        DataFrame with ``abate_amt`` and ``BSTCabate_amt`` columns.
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
    """Calculate maximum WFF entitlements before abatement.

    Args:
        df: DataFrame with WFF weight and eligibility columns.
        wff_params: Working for Families parameters.

    Returns:
        DataFrame with maximum entitlement columns.
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
    """Apply shared and unshared care logic to compute entitlements.

    Args:
        df: DataFrame containing maximum entitlement and abatement columns.
        wff_params: Working for Families parameters.

    Returns:
        DataFrame with calculated FTC, IWTC, BSTC and MFTC amounts.
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
    """Apply model calibrations to calculated entitlements.

    Currently sets IWTC to zero for self-employed individuals with no IWTC.

    Args:
        df: DataFrame with calculated entitlements.

    Returns:
        DataFrame with calibrations applied.
    """
    df = df.copy()
    df.loc[(df["iwtc"] == 0) & (df["selfempind"] == 1), "IWTCcalc"] = 0
    return df


def famsim(
    df: pd.DataFrame,
    wff_params: WFFParams,
    wagegwt: float,
    daysinperiod: int,
) -> pd.DataFrame:
    """Compose the WFF calculation phases using a rule engine.

    Args:
        df: DataFrame containing family information.
        wff_params: Working for Families parameters.
        wagegwt: Wage growth rate.
        daysinperiod: Number of days in the period.

    Returns:
        DataFrame with calculated WFF entitlements.
    """
    engine = RuleEngine(
        [
            Rule("gross_up_income", gross_up_income, {"wagegwt": wagegwt}),
            Rule(
                "calculate_abatement",
                calculate_abatement,
                {"wff_params": wff_params, "daysinperiod": daysinperiod},
            ),
            Rule(
                "calculate_max_entitlements",
                calculate_max_entitlements,
                {"wff_params": wff_params},
            ),
            Rule(
                "apply_care_logic",
                apply_care_logic,
                {"wff_params": wff_params},
            ),
            Rule("apply_calibrations", apply_calibrations),
        ]
    )

    return engine.run(df.copy())