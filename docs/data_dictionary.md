# Data Dictionary for WFF Microsimulation Model

This document provides a data dictionary for the Working for Families (WFF) microsimulation model, specifically detailing the inputs and outputs of the `famsim` function in `src/wff_microsim.py`.

## `famsim` Function Parameters

These are the scalar parameters passed directly to the `famsim` function, which define the policy settings and other model constants.

| Parameter Name | Type    | Description                                                                 |
| :------------- | :------ | :-------------------------------------------------------------------------- |
| `ftc1`         | `float` | FTC entitlement for the eldest child.                                       |
| `ftc2`         | `float` | FTC entitlement for subsequent children.                                    |
| `iwtc1`        | `float` | IWTC entitlement for 1-3 children.                                          |
| `iwtc2`        | `float` | IWTC entitlement for 4+ children.                                           |
| `bstc`         | `float` | BSTC entitlement.                                                           |
| `mftc`         | `float` | MFTC guaranteed income amount before tax (i.e., gross income).              |
| `abatethresh1` | `float` | First abatement threshold.                                                  |
| `abatethresh2` | `float` | Second abatement threshold (if any).                                        |
| `abaterate1`   | `float` | Abatement rate for the first abatement threshold.                           |
| `abaterate2`   | `float` | Abatement rate for the second abatement threshold.                          |
| `bstcthresh`   | `float` | Abatement threshold for BSTC.                                               |
| `bstcabate`    | `float` | Abatement rate for BSTC.                                                    |
| `wagegwt`      | `float` | Wage growth - growth in average ordinary weekly earnings on a March year basis. |
| `daysinperiod` | `int`   | Number of days in the period.                                               |

## `famsim` Input DataFrame Columns

These are the columns expected in the input pandas DataFrame (`df`) passed to the `famsim` function.

| Column Name         | Type      | Description                                                                 |
| :------------------ | :-------- | :-------------------------------------------------------------------------- |
| `familyinc`         | `float`   | Total family income.                                                        |
| `maxkiddays`        | `int`     | The maximum number of days a child is part of the family.                   |
| `maxkiddaysbstc`    | `int`     | The maximum number of days a child is eligible for BSTC.                    |
| `FTCwgt`            | `float`   | Weight for FTC calculation.                                                 |
| `IWTCwgt`           | `float`   | Weight for IWTC calculation.                                                |
| `iwtc_elig`         | `int`     | Flag indicating IWTC eligibility (1 if eligible, 0 otherwise).              |
| `BSTC0wgt`          | `float`   | Weight for BSTC for children under 1.                                       |
| `BSTC01wgt`         | `float`   | Weight for BSTC for children between 1 and 3.                               |
| `BSTC1wgt`          | `float`   | Weight for BSTC for children over 3.                                        |
| `pplcnt`            | `int`     | Number of people in the family.                                             |
| `MFTC_total`        | `float`   | Total MFTC amount.                                                          |
| `MFTC_elig`         | `int`     | Flag indicating MFTC eligibility (1 if eligible, 0 otherwise).              |
| `sharedcare`        | `int`     | Flag indicating if care is shared (1 if shared, 0 otherwise).               |
| `sharecareFTCwgt`   | `float`   | Weight for shared care FTC.                                                 |
| `sharecareBSTC0wgt` | `float`   | Weight for shared care BSTC for children under 1.                           |
| `sharecareBSTC01wgt`| `float`   | Weight for shared care BSTC for children between 1 and 3.                   |
| `sharecareBSTC1wgt` | `float`   | Weight for shared care BSTC for children over 3.                            |
| `MFTCwgt`           | `float`   | Weight for MFTC.                                                            |
| `iwtc`              | `float`   | IWTC amount.                                                                |
| `selfempind`        | `int`     | Flag indicating self-employment (1 if self-employed, 0 otherwise).          |

## `famsim` Output DataFrame Columns

These are the new columns added to the input DataFrame by the `famsim` function, containing the calculated WFF entitlements and intermediate values.

| Column Name            | Type    | Description                                                                 |
| :--------------------- | :------ | :-------------------------------------------------------------------------- |
| `familyinc_grossed_up` | `float` | Family income adjusted for wage growth.                                     |
| `abate_amt`            | `float` | The amount of abatement based on family income.                             |
| `BSTCabate_amt`        | `float` | The amount of abatement for Best Start Tax Credit.                          |
| `maxFTCent`            | `float` | Maximum Family Tax Credit entitlement.                                      |
| `maxIWTCent`           | `float` | Maximum In-Work Tax Credit entitlement.                                     |
| `maxBSTC0ent`          | `float` | Maximum Best Start Tax Credit entitlement for children under 1.             |
| `maxBSTC01ent`         | `float` | Maximum Best Start Tax Credit entitlement for children between 1 and 3.     |
| `maxBSTC1ent`          | `float` | Maximum Best Start Tax Credit entitlement for children over 3.              |
| `maxMFTCent`           | `float` | Maximum Minimum Family Tax Credit entitlement.                              |
| `FTCcalc`              | `float` | Calculated Family Tax Credit entitlement.                                   |
| `IWTCcalc`             | `float` | Calculated In-Work Tax Credit entitlement.                                  |
| `MFTCcalc`             | `float` | Calculated Minimum Family Tax Credit entitlement.                           |
| `BSTCcalc`             | `float` | Calculated Best Start Tax Credit entitlement.                               |
| `FTCcalcTEMP`          | `float` | Temporary calculation for FTC, used internally.                             |
| `carryforward_abate`   | `float` | Amount of abatement carried forward from FTC to IWTC calculation.           |
