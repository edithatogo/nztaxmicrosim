from __future__ import annotations

import math

from pydantic import BaseModel

from .investment_tax import calculate_pie_tax
from .microsim import load_parameters, simrwt, taxit
from .parameters import (
    FamilyBoostParams,
    Parameters,
    PIEParams,
    RWTParams,
    TaxBracketParams,
)
from .tax_credits import calcietc, eitc, family_boost_credit


class TaxCalculator(BaseModel):
    """Convenience wrapper around core tax calculations.

    The class stores a set of policy parameters and exposes small helper
    methods which delegate to the functions defined in :mod:`microsim`.
    """

    params: Parameters

    def income_tax(self, taxable_income: float) -> float:
        """
        Calculate income tax for a given taxable income.

        This method uses a progressive tax system with multiple tax brackets.
        The tax rates and thresholds for these brackets are drawn from
        `params.tax_brackets`.

        The calculation is performed by the `taxit` function.

        Args:
            taxable_income: The amount of income to calculate tax on.

        Returns:
            The amount of income tax payable.
        """
        tax_params: TaxBracketParams = self.params.tax_brackets
        return taxit(taxy=taxable_income, params=tax_params)

    def ietc(
        self,
        taxable_income: float,
        is_wff_recipient: bool,
        is_super_recipient: bool,
        is_benefit_recipient: bool,
    ) -> float:
        """
        Calculate the Independent Earner Tax Credit (IETC).

        The IETC is a tax credit for individuals who are not receiving
        certain other benefits, such as Working for Families or NZ Super.

        The calculation is performed by the `calcietc` function.

        Args:
            taxable_income: The individual's taxable income.
            is_wff_recipient: Whether the individual is a recipient of
                Working for Families tax credits.
            is_super_recipient: Whether the individual is a recipient of
                NZ Superannuation.
            is_benefit_recipient: Whether the individual is a recipient of
                a main benefit.

        Returns:
            The amount of IETC the individual is entitled to.
        """
        return calcietc(
            taxable_income=taxable_income,
            is_wff_recipient=is_wff_recipient,
            is_super_recipient=is_super_recipient,
            is_benefit_recipient=is_benefit_recipient,
            ietc_params=self.params.ietc,
        )

    def rwt(self, interest: float, taxable_income: float) -> float:
        """
        Calculate Resident Withholding Tax (RWT) on interest income.

        RWT is a tax on interest earned from sources like bank accounts and
        investments. The tax rate depends on the individual's income tax
        bracket. This method determines the correct RWT rate based on the
        provided taxable income and then calculates the RWT amount.

        Args:
            interest: The amount of interest income subject to RWT.
            taxable_income: The individual's total taxable income, used to
                determine the RWT rate.

        Returns:
            The amount of RWT payable.
        """
        tax_brackets = self.params.tax_brackets
        rwt_rates = self.params.rwt

        # Determine the marginal tax rate to find the corresponding RWT rate.
        # The last rate in the list applies to all income above the last threshold.
        rate = tax_brackets.rates[-1]
        for i, threshold in enumerate(tax_brackets.thresholds):
            if taxable_income <= threshold:
                rate = tax_brackets.rates[i]
                break

        # Map the income tax rate to the corresponding RWT rate.
        rwt_rate = 0.0
        if math.isclose(rate, 0.105):
            rwt_rate = rwt_rates.rwt_rate_10_5
        elif math.isclose(rate, 0.175):
            rwt_rate = rwt_rates.rwt_rate_17_5
        elif math.isclose(rate, 0.30):
            rwt_rate = rwt_rates.rwt_rate_30
        elif math.isclose(rate, 0.33):
            rwt_rate = rwt_rates.rwt_rate_33
        elif math.isclose(rate, 0.39):
            rwt_rate = rwt_rates.rwt_rate_39

        return simrwt(interest, rwt_rate)

    def family_boost_credit(self, family_income: float, childcare_costs: float) -> float:
        """
        Calculates the FamilyBoost childcare tax credit.

        Args:
            family_income: The total family income.
            childcare_costs: The total childcare costs for the period.

        Returns:
            The calculated FamilyBoost credit amount.
        """
        return family_boost_credit(
            family_income=family_income,
            childcare_costs=childcare_costs,
            family_boost_params=self.params.family_boost,
        )

    def eitc(
        self,
        is_credit_enabled: bool,
        is_eligible: bool,
        income: float,
        min_income_threshold: float,
        max_entitlement_income: float,
        abatement_income_threshold: float,
        earning_rate: float,
        abatement_rate: float,
    ) -> float:
        """
        Calculates the Earned Income Tax Credit (EITC).

        Args:
            is_credit_enabled: Flag to enable or disable the credit calculation.
            is_eligible: Flag indicating if the individual is eligible for the credit.
            income: The income amount to base the calculation on.
            min_income_threshold: The income level at which the credit begins.
            max_entitlement_income: The income level where the credit reaches its maximum.
            abatement_income_threshold: The income level at which the credit begins to abate.
            earning_rate: The rate at which the credit is earned during phase-in.
            abatement_rate: The rate at which the credit is reduced during phase-out.

        Returns:
            The calculated EITC amount.
        """
        return eitc(
            is_credit_enabled=is_credit_enabled,
            is_eligible=is_eligible,
            income=income,
            min_income_threshold=min_income_threshold,
            max_entitlement_income=max_entitlement_income,
            abatement_income_threshold=abatement_income_threshold,
            earning_rate=earning_rate,
            abatement_rate=abatement_rate,
        )

    def pie_tax(self, pie_income: float, taxable_income: float) -> float:
        """
        Calculates tax on Portfolio Investment Entity (PIE) income.

        Args:
            pie_income: The income from the PIE investment.
            taxable_income: The individual's total taxable income for the year,
                used to determine the Prescribed Investor Rate (PIR).

        Returns:
            The calculated tax on the PIE income. Returns 0 if PIE parameters
            are not available for the year.
        """
        if self.params.pie is None:
            return 0.0

        return calculate_pie_tax(
            pie_income=pie_income,
            taxable_income=taxable_income,
            pie_params=self.params.pie,
        )

    @classmethod
    def from_year(cls, year: str) -> "TaxCalculator":
        """
        Construct a :class:`TaxCalculator` from stored parameter files.

        This method loads the parameters for a given tax year from the
        corresponding JSON file (e.g., `parameters_2023-2024.json`).

        Args:
            year: The tax year to load parameters for (e.g., "2023-2024").

        Returns:
            A new `TaxCalculator` instance with the loaded parameters.
        """
        params = load_parameters(year)
        return cls(params=params)
