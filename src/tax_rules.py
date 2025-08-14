"""Rules for tax calculations."""

from dataclasses import dataclass
from typing import Any

from .acc_levy import calculate_acc_levy
from .parameters import ACCLevyParams, KiwisaverParams, StudentLoanParams
from .pipeline import Rule, register_rule


@register_rule
@dataclass
class ACCLevyRule(Rule):
    """A rule to calculate the ACC (Accident Compensation Corporation) levy.

    The ACC levy is a compulsory payment that helps fund the cost of accidents
    in New Zealand. This rule calculates the levy based on an individual's
    income, up to a maximum income threshold.

    The calculation is performed by the `calculate_acc_levy` function.
    """

    acc_levy_params: ACCLevyParams | None
    name: str = "acc_levy"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculate ACC levy and add it to the DataFrame.

        This method applies the `calculate_acc_levy` function to the
        `familyinc` column of the DataFrame in the `data` dictionary
        and stores the result in a new `acc_levy` column.

        Args:
            data: The data dictionary, expected to contain a 'df' key with
                a pandas DataFrame. The DataFrame must contain a 'familyinc'
                column.
        """
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


@register_rule
@dataclass
class KiwiSaverRule(Rule):
    """A rule to calculate KiwiSaver contributions.

    KiwiSaver is a voluntary savings scheme to help New Zealanders save for
    their retirement. This rule calculates the employee's contribution based
    on their income and a specified contribution rate.

    The calculation is performed by the `calculate_kiwisaver_contribution`
    function.
    """

    kiwisaver_params: KiwisaverParams | None
    name: str = "kiwisaver"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculate KiwiSaver contribution and add it to the DataFrame.

        This method applies the `calculate_kiwisaver_contribution` function
        to the `familyinc` column of the DataFrame in the `data` dictionary
        and stores the result in a new `kiwisaver_contribution` column.

        Args:
            data: The data dictionary, expected to contain a 'df' key with
                a pandas DataFrame. The DataFrame must contain a 'familyinc'
                column.
        """
        if not self.kiwisaver_params:
            return
        from .payroll_deductions import calculate_kiwisaver_contribution

        df = data["df"]
        df["kiwisaver_contribution"] = df["familyinc"].apply(
            lambda income: calculate_kiwisaver_contribution(
                income=income,
                rate=self.kiwisaver_params.contribution_rate,
            )
        )


@register_rule
@dataclass
class StudentLoanRule(Rule):
    """A rule to calculate student loan repayments.

    This rule calculates the amount of student loan repayment required based
    on an individual's income. Repayments are only required if the income is
    above a certain threshold.

    The calculation is performed by the `calculate_student_loan_repayment`
    function.
    """

    student_loan_params: StudentLoanParams | None
    name: str = "student_loan"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculate student loan repayment and add it to the DataFrame.

        This method applies the `calculate_student_loan_repayment` function
        to the `familyinc` column of the DataFrame in the `data` dictionary
        and stores the result in a new `student_loan_repayment` column.

        Args:
            data: The data dictionary, expected to contain a 'df' key with
                a pandas DataFrame. The DataFrame must contain a 'familyinc'
                column.
        """
        if not self.student_loan_params:
            return
        from .payroll_deductions import calculate_student_loan_repayment

        df = data["df"]
        df["student_loan_repayment"] = df["familyinc"].apply(
            lambda income: calculate_student_loan_repayment(
                income=income,
                repayment_threshold=self.student_loan_params.repayment_threshold,
                repayment_rate=self.student_loan_params.repayment_rate,
            )
        )


@register_rule
@dataclass
class IETCRule(Rule):
    """A rule to calculate the Independent Earner Tax Credit (IETC).

    The IETC is a tax credit for individuals who are not receiving certain
    other benefits. This rule determines the eligibility for and calculates
    the amount of the IETC for each individual.

    The calculation is performed by the `ietc` method of the `TaxCalculator`
    class.
    """

    name: str = "ietc"
    enabled: bool = True

    def __call__(self, data: dict[str, Any]) -> None:
        """Calculate IETC and add it to the DataFrame.

        This method uses the `TaxCalculator` to determine the IETC amount
        based on the individual's income and benefit status. The result is
        stored in a new `ietc` column.

        Args:
            data: The data dictionary, expected to contain a 'df' key with
                a pandas DataFrame and a 'params' key with the simulation
                parameters. The DataFrame must contain 'familyinc' and
                benefit recipient columns (e.g., 'is_jss_recipient').
        """
        if not data["params"].ietc:
            return
        from .tax_calculator import TaxCalculator

        df = data["df"]
        tax_calc = TaxCalculator(params=data["params"])
        df["ietc"] = df.apply(
            lambda row: tax_calc.ietc(
                taxable_income=row["familyinc"],
                is_wff_recipient=row["FTCcalc"] > 0,
                is_super_recipient=row["is_nz_super_recipient"],
                is_benefit_recipient=row["is_jss_recipient"] or row["is_sps_recipient"] or row["is_slp_recipient"],
            ),
            axis=1,
        )
