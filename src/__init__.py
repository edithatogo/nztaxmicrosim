"""NZ tax microsimulation package.

This package exposes modules without importing optional heavy dependencies at
import time. Only a minimal set of symbols are re-exported here.
"""

from .tax_calculator import TaxCalculator

__all__ = ["TaxCalculator"]
