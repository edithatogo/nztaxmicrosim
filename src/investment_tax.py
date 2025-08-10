from __future__ import annotations

from .parameters import PIEParams


def calculate_pie_tax(
    pie_income: float,
    taxable_income: float,
    pie_params: PIEParams,
) -> float:
    """
    Calculates tax on Portfolio Investment Entity (PIE) income.

    This function determines the Prescribed Investor Rate (PIR) based on the
    individual's taxable income and then calculates the tax on the PIE income.

    .. warning::
        The current implementation uses a simplified logic based on a single
        year's income to determine the PIR. The official IRD rules require
        looking at income from the two preceding years. This implementation
        should be updated when the definitive two-year lookback logic is
        clarified.

    Args:
        pie_income: The income from the PIE investment.
        taxable_income: The individual's total taxable income for the year.
        pie_params: The parameters for PIE tax, including rates and thresholds.

    Returns:
        The calculated tax on the PIE income.
    """
    if pie_income <= 0:
        return 0.0

    total_income = taxable_income + pie_income

    # Determine the PIR rate based on income thresholds.
    # This is a simplified logic. The official rules are more complex.
    pir = pie_params.rates[-1]  # Default to the highest rate
    for i, taxable_thresh in enumerate(pie_params.taxable_income_thresholds):
        if taxable_income <= taxable_thresh:
            if total_income <= pie_params.taxable_plus_pie_income_thresholds[i]:
                pir = pie_params.rates[i]
                break

    return pie_income * pir
