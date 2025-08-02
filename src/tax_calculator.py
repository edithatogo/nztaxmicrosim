from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from .microsim import calcietc, load_parameters, simrwt, taxit
from .parameters import Parameters


@dataclass
class TaxCalculator:
    """Convenience wrapper around core tax calculations.

    The class stores a set of policy parameters and exposes small helper
    methods which delegate to the functions defined in :mod:`microsim`.
    """

    params: Parameters
    rwt_params: Optional[Dict[str, float]] = None

    def income_tax(self, taxable_income: float) -> float:
        """Calculate income tax for a given taxable income.

        Parameters are drawn from ``params.tax_brackets``.
        """
        return taxit(taxy=taxable_income, params=self.params.tax_brackets)

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

    def rwt(self, interest: float) -> float:
        """Calculate Resident Withholding Tax on interest income."""
        rwt_params = self.rwt_params or {}
        return simrwt(
            interest=interest,
            rwt_rate_10_5=rwt_params.get("rwt_rate_10_5", 0.0),
            rwt_rate_17_5=rwt_params.get("rwt_rate_17_5", 0.0),
            rwt_rate_30=rwt_params.get("rwt_rate_30", 0.0),
            rwt_rate_33=rwt_params.get("rwt_rate_33", 0.0),
            rwt_rate_39=rwt_params.get("rwt_rate_39", 0.0),
        )

    @classmethod
    def from_year(cls, year: str) -> "TaxCalculator":
        """Construct a :class:`TaxCalculator` from stored parameter files."""
        params = load_parameters(year)
        return cls(params)
