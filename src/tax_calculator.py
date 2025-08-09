from __future__ import annotations

from typing import Dict

from pydantic import BaseModel

from .microsim import calcietc, load_parameters, simrwt, taxit
from .parameters import Parameters, RWTParams, TaxBracketParams


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

    def rwt(self, interest: float, rwt_params: RWTParams | None = None) -> float:
        """
        Calculate Resident Withholding Tax (RWT) on interest income.

        RWT is a tax on interest earned from sources like bank accounts and
        investments. The tax rate depends on the individual's income tax
        bracket.

        The calculation is performed by the `simrwt` function.

        Args:
            interest: The amount of interest income.
            rwt_params: Optional. The RWT parameters to use. If not
                provided, the parameters from `self.params.rwt` will be
                used.

        Returns:
            The amount of RWT payable.
        """
        if rwt_params is None:
            rwt_params = self.params.rwt
        return simrwt(interest, rwt_params)

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
