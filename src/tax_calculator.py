from __future__ import annotations

from typing import Dict

from pydantic import BaseModel

from .microsim import calcietc, load_parameters, simrwt, taxit
from .parameters import Parameters, TaxBracketParams


class TaxCalculator(BaseModel):
    """Convenience wrapper around core tax calculations.

    The class stores a set of policy parameters and exposes small helper
    methods which delegate to the functions defined in :mod:`microsim`.
    """

    params: Parameters

    def income_tax(self, taxable_income: float) -> float:
        """Calculate income tax for a given taxable income.

        Parameters are drawn from ``params.tax_brackets``.
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
        """Calculate the Independent Earner Tax Credit (IETC)."""
        return calcietc(
            taxable_income=taxable_income,
            is_wff_recipient=is_wff_recipient,
            is_super_recipient=is_super_recipient,
            is_benefit_recipient=is_benefit_recipient,
            ietc_params=self.params.ietc,
        )

    def rwt(self, interest: float, rwt_params=None) -> float:
        """Calculate Resident Withholding Tax on interest income."""
        if rwt_params is None:
            rwt_params = self.params.rwt
        return simrwt(interest, rwt_params)

    @classmethod
    def from_year(cls, year: str) -> "TaxCalculator":
        """Construct a :class:`TaxCalculator` from stored parameter files."""
        params = load_parameters(year)
        return cls(params=params)
