"""Rules for tax calculations."""

from dataclasses import dataclass
from typing import Any

from .acc_levy import calculate_acc_levy
from .pipeline import Rule
try:
    from .parameters import ACCLevyParams
except ImportError:
    ACCLevyParams = None

@dataclass
class ACCLevyRule(Rule):
    """Rule to calculate ACC levy."""

    acc_levy_params: ACCLevyParams
    name: str = "acc_levy"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculates the ACC levy and adds it to the DataFrame."""
        if not self.acc_levy_params:
            return
        df = data["df"]
        df["acc_levy"] = df["familyinc"].apply(
            lambda income: calculate_acc_levy(
                income=income,
                levy_rate=self.acc_levy_params.rate,
                max_income=self.acc_levy_params.max_income,
            )
        )


@dataclass
class KiwiSaverRule(Rule):
    """Rule to calculate KiwiSaver contributions."""

    kiwisaver_params: "KiwisaverParams"
    name: str = "kiwisaver"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculates the KiwiSaver contribution and adds it to the DataFrame."""
        from .payroll_deductions import calculate_kiwisaver_contribution

        df = data["df"]
        df["kiwisaver_contribution"] = df["familyinc"].apply(
            lambda income: calculate_kiwisaver_contribution(
                income=income,
                rate=self.kiwisaver_params.contribution_rate,
            )
        )


@dataclass
class StudentLoanRule(Rule):
    """Rule to calculate student loan repayments."""

    student_loan_params: "StudentLoanParams"
    name: str = "student_loan"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculates the student loan repayment and adds it to the DataFrame."""
        from .payroll_deductions import calculate_student_loan_repayment

        df = data["df"]
        df["student_loan_repayment"] = df["familyinc"].apply(
            lambda income: calculate_student_loan_repayment(
                income=income,
                repayment_threshold=self.student_loan_params.repayment_threshold,
                repayment_rate=self.student_loan_params.repayment_rate,
            )
        )


@dataclass
class IETCRule(Rule):
    """Rule to calculate the Independent Earner Tax Credit."""

    name: str = "ietc"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculates the IETC and adds it to the DataFrame."""
        from .tax_calculator import TaxCalculator

        df = data["df"]
        tax_calc = TaxCalculator(params=data["params"])
        df["ietc"] = df.apply(
            lambda row: tax_calc.ietc(
                taxable_income=row["familyinc"],
                is_wff_recipient=row["FTCcalc"] > 0,
                is_super_recipient=row["is_nz_super_recipient"],
                is_benefit_recipient=row["is_jss_recipient"]
                or row["is_sps_recipient"]
                or row["is_slp_recipient"],
            ),
            axis=1,
        )
