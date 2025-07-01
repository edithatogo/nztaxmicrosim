[IN CONFIDENCE RELEASE EXTERNAL]
**WFF micro simulation model**
The microsimulation model is used in both calibrating the model results to actual entitlements for
the tax year as well as projecting costs for future tax years for common parameter changes.
The microsimulation model can be used in the following ways:
* Impact of changes to entitlements e.g. increase FTC, IWTC, BSTC or MFTC guaranteed income
amount
* Changes to abatement rates and thresholds for FTC/IWTC and BSTC
* Introducing a second abatement tier for FTC and IWTC
* Measuring the impact on WFF payments from changes in income
Program name: s 18(c)(i) sas
The 2023 represents the tax year the data is built from.
The model is structured as a macro, thereby making it easier to run multiple simulations with
different changes in the input parameters. The macro input variables are structured as
famsim(ftc1,ftc2,iwtc1,iwtc2,bstc,mftc,abatethresh1,abatethresh2,abaterate1,abaterate2,bstcthresh,
bstcabate,wagegwt)
With the input variables comprising:
* ftc1 = Unabated FTC entitlement for eldest child
* ftc2 = Unabated FTC entitlement for subsequent child
* iwtc1 = IWTC entitlement for 1-3 children
* iwtc2 = IWTC entitlement for 4+ children
* bstc = BSTC entitlement
* mftc = MFTC guaranteed income amount before tax (ie gross income)
* abatethresh1 = first FTC/IWTC abatement threshold
* abatethresh2 = second FTC/IWTC abatement threshold (if any)
* abaterate1 = abatement rate for the first FTC/IWTC abatement threshold
* abaterate2 = abatement rate for the second FTC/IWTC abatement threshold
* bstcabate = abatement threshold for BSTC
* bstcabater = abatement rate for BSTC
* wagegwt = wage growth - growth in average ordinary weekly earnings on a March year basis
The model is structured around 5 sections:
1. Projecting income in the forecast period
2. Calculating abatement
3. Calculating entitlements (before abatement)
4. Calculating the abated entitlement
5. Calibrations
[IN CONFIDENCE RELEASE EXTERNAL]
**1. Projecting income in the forecast period**
Family scheme income is projected into the forecast period by increasing the income amount by a
user defined growth rate (wagegwt), expressed as a decimal e.g. 6% would be defined at 0.06.
All income types are projected using the same growth parameter.
Future iterations of the model will enable different rates of growth percentages to be applied to
different types of income, e.g. growing benefits at the rate of CPI rather than wage growth.
Within the WFF scheme, year on year family income can grow at a faster rate than a base multiplier,
and can fall. In 2022, family scheme income grew faster than the population average for all income
for families with incomes under $70,000, while family scheme income for families with incomes
greater than $70,000 grew at a slower rate than the base multiplier and for some families it was
negative. This reflected a shortage of unskilled labour in that year following the reopening of the
economy post covid. Therefore, a major limitation of the model is applying a static rate of income
growth to all individuals in the WFF population.
Future enhancements of the model could look at introducing income multipliers so that the growth
rates could range from -3x the multiplier to +3x the multiplier as well as randomly doubling the
number of families to achieve population growth
**2. Calculating potential abatement**
The model has two abatement thresholds set for modelling abatement of FTC and IWTC and one
abatement threshold set for modelling BSTC.
For abatement of FTC and IWTC the model calculates the abatement as:
* If family scheme income is less than the lowest abatement tier, then abatement is $0
* If family scheme income is between the 2 abatement tiers, then abatement amount is
(family scheme income – first abatement tier) * abatement rate for first tier
* If family scheme income is above the second abatement tier, then abatement amount is
calculated as
(second abatement tier – first abatement tier) * abatement rate for first tier +
(family scheme income – second abatement tier) * abatement rate for second tier
For abatement of BSTC for children that are more than 12 months old, the model calculates
abatement as:
* If family scheme income is less than the BSTC abatement tier, then abatement is $0
* If family scheme income is above the BSTC abatement tier, then abatement amount is
(family scheme income – abatement tier) * abatement rate
For both abatement calculations, if the maximum length of time that a child in the WFF scheme is
less than 365 days, then the abatement amount is scaled down by the maximum number of kid days
/ 365. This reflects the system prorating the abatement into the relationship period and mirrors the
methodology used in calculating entitlements using child weights in the section below.
[IN CONFIDENCE RELEASE EXTERNAL]
**3. Calculating entitlements (before abatement)**
Child weights were calculated in Part B of the model, with separate weights developed for FTC, IWTC,
BSTC (0-1 year and 1year +) and MFTC. The weights reflect the time that the child was included in the
family. These weights are used to determine the entitlement for each tax credit.
FTC entitlement
If the FTC child weight is less than 1 (ie the child has been enrolled in the WFF program for less than
12 months) then the FTC entitlement amount is calculated as:
FTCwgt * eldest child entitlement amount
Where the FTC child weight is greater than 1 then the FTC entitlement amount is calculated as:
Eldest child entitlement amount + subsequent child entitlement amount * (FTCwgt – 1)
IWTC entitlement
The number of months the family is entitlement to IWTC to has been calculated in Part B.
If the IWTC child weight is less than 1, then the IWTC entitlement amount is calculated as:
IWTC entitlement < 3 children * IWTCwgt * number of months eligible / 12
If the IWTC child weight is less than or equal to 3, then the IWTC entitlement amount is calculated as:
IWTC entitlement < 3 children * number of months eligible / 12
If the IWTC child weight is greater than 3, then the IWTC entitlement amount is calculated as:
(IWTC entitlement < 3 children + (IWTCwgt – 3) * IWTC entitlement 4+ children)
* number of months eligible / 12
BSTC entitlement
The maximum BSTC entitlement for children aged 0-1 is calculated as:
BSTC entitlement per child * (BSTC0wgt – number of fortnights receiving PPL / 26) with a
minimum value of $0
The maximum entitlement for children aged 1-3 id calculated as:
BSTC entitlement per child * BSTC1wgt
MFTC entitlement
In Part B, a MFTC entitlement was calculated for everyone on a per month basis. A value would be
created if their wage and salary income (excluding payments from a company they own) before was
less than the pretax monthly MFTC guaranteed income amount.
[IN CONFIDENCE RELEASE EXTERNAL]
The MFTC entitlement is calculated for families with annual family scheme income less than the
MFTC guaranteed income amount (before tax) and the total amount of MFTC calculated on a
monthly basis is greater than 0 and if calculated MFTC eligibility is greater than 0. The amount of
MFTC they are eligible for is calculated as the lessor of:
* The total of the calculated MFTC monthly amount calculated in Part B summed over the
year, or
* The MFTC guaranteed income amount (before tax) less family scheme income * (1 –
personal income tax of 17.5%)
The final calculation is reduced by shared care (MFTCwgt), if any.
**4. Calculated entitlement after abatement**
If there are no children with shared care arrangements in the family then final entitlements are
calculated as:
* FTC entitlement less FTC/IWTC abatement amount. If the FTC/IWTC abatement amount is
greater than the FTC entitlement then the FTC entitlement is $0 and any remaining
abatement amount is carried forward into the IWTC calculation
* IWTC entitlement less any carry forward FTC/IWTC abatement
* BSTC entitlement for 0-1 child plus (BSTC entitlement for children aged 1+ less BSTC
abatement for children aged 1+, with a minimum value of $0)
* MFTC entitlement is equal to the entitlement calculated directly above
If there are children with shared care arrangements, then each of the entitlements calculated above
under the no shared care approach is adjusted for shared care.
**5. Calibrations**
One calibration has been introduced into the model.
Where the IWTC paid for the tax year is equal to $0 and the family has at least one person self
employed, it is assumed that IR has otherwise determined that the family is not entitled to IWTC.
Therefore, any IWTC amount calculated for the family by the model is set to $0.
