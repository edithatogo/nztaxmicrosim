"""NZ tax microsimulation package.

This package exposes modules without importing optional heavy dependencies at
import time. Only a minimal set of symbols are re-exported here.
"""

from .acc_levy import calculate_acc_levy, calculate_payroll_deductions
from .optimisation import run_parameter_scan, run_policy_optimisation
from .pipeline import Rule, SimulationPipeline
from .sensitivity_analysis import (
    run_deterministic_analysis,
    run_probabilistic_analysis,
)
from .tax_calculator import TaxCalculator
from .tax_rules import IETCRule, IncomeTaxRule
from .value_of_information import calculate_evpi, calculate_evppi

__all__ = [
    "calculate_evpi",
    "calculate_evppi",
    "calculate_acc_levy",
    "calculate_payroll_deductions",
    "run_deterministic_analysis",
    "run_probabilistic_analysis",
    "run_parameter_scan",
    "run_policy_optimisation",
    "TaxCalculator",
    "Rule",
    "SimulationPipeline",
    "IncomeTaxRule",
    "IETCRule",
]
