"""Rules for tax calculations."""

from dataclasses import dataclass
from typing import Any

from .acc_levy import calculate_acc_levy
from .rule_registry import Rule, register_rule


@register_rule
@dataclass
class ACCLevyRule(Rule):
    """A rule to calculate the ACC (Accident Compensation Corporation) levy."""

    name: str = "ACCLevyRule"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculate ACC levy and add it to the DataFrame."""
        acc_levy_params = data["params"].acc_levy
        if not acc_levy_params:
            return
        df = data["df"]
        df["acc_levy"] = df["familyinc"].apply(
            lambda income: calculate_acc_levy(
                income=income,
                levy_rate=acc_levy_params.rate,
                max_income=acc_levy_params.max_income,
            )
        )


@register_rule
@dataclass
class KiwiSaverRule(Rule):
    """A rule to calculate KiwiSaver contributions."""

    name: str = "KiwiSaverRule"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculate KiwiSaver contribution and add it to the DataFrame."""
        kiwisaver_params = data["params"].kiwisaver
        if not kiwisaver_params:
            return
        from .payroll_deductions import calculate_kiwisaver_contribution

        df = data["df"]
        df["kiwisaver_contribution"] = df["familyinc"].apply(
            lambda income: calculate_kiwisaver_contribution(
                income=income,
                rate=kiwisaver_params.contribution_rate,
            )
        )


@register_rule
@dataclass
class StudentLoanRule(Rule):
    """A rule to calculate student loan repayments."""

    name: str = "StudentLoanRule"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculate student loan repayment and add it to the DataFrame."""
        student_loan_params = data["params"].student_loan
        if not student_loan_params:
            return
        from .payroll_deductions import calculate_student_loan_repayment

        df = data["df"]
        df["student_loan_repayment"] = df["familyinc"].apply(
            lambda income: calculate_student_loan_repayment(
                income=income,
                repayment_threshold=student_loan_params.repayment_threshold,
                repayment_rate=student_loan_params.repayment_rate,
            )
        )


@register_rule
@dataclass
class IncomeTaxRule(Rule):
    """A rule to calculate income tax."""

    name: str = "IncomeTaxRule"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculate income tax and add it to the DataFrame."""
        df = data["df"]
        tax_calc = data["tax_calc"]
        df["tax_liability"] = df["familyinc"].apply(tax_calc.income_tax)


@register_rule
@dataclass
class IETCRule(Rule):
    """A rule to calculate the Independent Earner Tax Credit (IETC)."""

    name: str = "IETCRule"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculate IETC and add it to the DataFrame."""
        if not data["params"].ietc:
            return

        df = data["df"]
        tax_calc = data["tax_calc"]
        df["ietc"] = df.apply(
            lambda row: tax_calc.ietc(
                taxable_income=row["familyinc"],
                is_wff_recipient=row.get("FTCcalc", 0) > 0,
                is_super_recipient=row.get("is_nz_super_recipient", False),
                is_benefit_recipient=(
                    row.get("is_jss_recipient", False)
                    or row.get("is_sps_recipient", False)
                    or row.get("is_slp_recipient", False)
                ),
            ),
            axis=1,
        )
