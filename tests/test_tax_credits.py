from __future__ import annotations

import pytest

from src.tax_credits import (
    calculate_donation_credit,
    calcietc,
    eitc,
    family_boost_credit,
)
from src.parameters import (
    DonationCreditParams,
    FamilyBoostParams,
    IETCParams,
)
from src.microsim import load_parameters

# Load parameters for testing
params_2022_23 = load_parameters("2022-2023")
params_2024_25 = load_parameters("2024-2025")


def test_calcietc():
    """
    Tests the calcietc function for IETC calculation.
    """
    ietc_params = params_2022_23.ietc

    # Test case 1: Eligible for the full credit.
    assert (
        calcietc(
            taxable_income=30000,
            is_wff_recipient=False,
            is_super_recipient=False,
            is_benefit_recipient=False,
            ietc_params=ietc_params,
        )
        == 520
    )

    # Test case 2: Eligible for the abated credit.
    assert (
        calcietc(
            taxable_income=49000,
            is_wff_recipient=False,
            is_super_recipient=False,
            is_benefit_recipient=False,
            ietc_params=ietc_params,
        )
        > 0
    )  # Abated credit
    assert (
        calcietc(
            taxable_income=49000,
            is_wff_recipient=False,
            is_super_recipient=False,
            is_benefit_recipient=False,
            ietc_params=ietc_params,
        )
        < 520
    )  # Less than full credit

    # Test case 3: Not eligible (income too low).
    assert (
        calcietc(
            taxable_income=20000,
            is_wff_recipient=False,
            is_super_recipient=False,
            is_benefit_recipient=False,
            ietc_params=ietc_params,
        )
        == 0
    )

    # Test case 4: Not eligible (receiving WFF).
    assert (
        calcietc(
            taxable_income=30000,
            is_wff_recipient=True,
            is_super_recipient=False,
            is_benefit_recipient=False,
            ietc_params=ietc_params,
        )
        == 0
    )

    # Test case 5: Not eligible (receiving superannuation).
    assert (
        calcietc(
            taxable_income=30000,
            is_wff_recipient=False,
            is_super_recipient=True,
            is_benefit_recipient=False,
            ietc_params=ietc_params,
        )
        == 0
    )

    # Test case 6: Not eligible (receiving a main benefit).
    assert (
        calcietc(
            taxable_income=30000,
            is_wff_recipient=False,
            is_super_recipient=False,
            is_benefit_recipient=True,
            ietc_params=ietc_params,
        )
        == 0
    )


def test_eitc():
    """
    Tests the eitc function for Earned Income Tax Credit calculation.
    """
    # Test case 1: Earning zone
    assert (
        eitc(
            is_credit_enabled=True,
            is_eligible=True,
            income=10000,
            min_income_threshold=5000,
            max_entitlement_income=15000,
            abatement_income_threshold=20000,
            earning_rate=0.1,
            abatement_rate=0.2,
        )
        == 500
    )

    # Test case 2: Stable zone
    assert (
        eitc(
            is_credit_enabled=True,
            is_eligible=True,
            income=18000,
            min_income_threshold=5000,
            max_entitlement_income=15000,
            abatement_income_threshold=20000,
            earning_rate=0.1,
            abatement_rate=0.2,
        )
        == 1000
    )

    # Test case 3: Abatement zone
    assert eitc(
        is_credit_enabled=True,
        is_eligible=True,
        income=22000,
        min_income_threshold=5000,
        max_entitlement_income=15000,
        abatement_income_threshold=20000,
        earning_rate=0.1,
        abatement_rate=0.2,
    ) == max(0, 1000 - (22000 - 20000) * 0.2)

    # Test case 4: Not eligible
    assert (
        eitc(
            is_credit_enabled=True,
            is_eligible=False,
            income=10000,
            min_income_threshold=5000,
            max_entitlement_income=15000,
            abatement_income_threshold=20000,
            earning_rate=0.1,
            abatement_rate=0.2,
        )
        == 0
    )

    # Test case 5: Credit not on
    assert (
        eitc(
            is_credit_enabled=False,
            is_eligible=True,
            income=10000,
            min_income_threshold=5000,
            max_entitlement_income=15000,
            abatement_income_threshold=20000,
            earning_rate=0.1,
            abatement_rate=0.2,
        )
        == 0
    )


def test_family_boost_credit():
    """
    Tests the family_boost_credit function with various scenarios.
    """
    family_boost_params = params_2024_25.family_boost

    # Test case 1: Income below threshold, credit is 25% of costs
    assert family_boost_credit(100000, 1000, family_boost_params) == 250

    # Test case 2: Income below threshold, credit is capped at max_credit
    assert family_boost_credit(100000, 20000, family_boost_params) == family_boost_params.max_credit

    # Test case 3: Income above threshold, credit is abated
    credit = min(10000 * 0.25, family_boost_params.max_credit)
    abatement = (150000 - family_boost_params.income_threshold) * family_boost_params.abatement_rate
    expected_credit = max(0, credit - abatement)
    assert family_boost_credit(150000, 10000, family_boost_params) == expected_credit

    # Test case 4: Income above max_income, credit is 0
    assert family_boost_credit(190000, 10000, family_boost_params) == 0


def test_calcietc_new():
    """Test the calcietc function."""
    ietc_params = IETCParams(
        thrin=24000,
        ent=520,
        thrab=48000,
        abrate=0.13,
    )

    # Test case 1: Not eligible due to being a WFF recipient
    assert (
        calcietc(
            taxable_income=30000,
            is_wff_recipient=True,
            is_super_recipient=False,
            is_benefit_recipient=False,
            ietc_params=ietc_params,
        )
        == 0
    )

    # Test case 2: Not eligible due to being a superannuation recipient
    assert (
        calcietc(
            taxable_income=30000,
            is_wff_recipient=False,
            is_super_recipient=True,
            is_benefit_recipient=False,
            ietc_params=ietc_params,
        )
        == 0
    )

    # Test case 3: Not eligible due to being a main benefit recipient
    assert (
        calcietc(
            taxable_income=30000,
            is_wff_recipient=False,
            is_super_recipient=False,
            is_benefit_recipient=True,
            ietc_params=ietc_params,
        )
        == 0
    )

    # Test case 4: Not eligible due to income being too low
    assert (
        calcietc(
            taxable_income=20000,
            is_wff_recipient=False,
            is_super_recipient=False,
            is_benefit_recipient=False,
            ietc_params=ietc_params,
        )
        == 0
    )

    # Test case 5: Eligible for maximum entitlement
    assert (
        calcietc(
            taxable_income=30000,
            is_wff_recipient=False,
            is_super_recipient=False,
            is_benefit_recipient=False,
            ietc_params=ietc_params,
        )
        == 520
    )

    # Test case 6: Eligible for abated entitlement
    assert (
        calcietc(
            taxable_income=50000,
            is_wff_recipient=False,
            is_super_recipient=False,
            is_benefit_recipient=False,
            ietc_params=ietc_params,
        )
        == 520 - (50000 - 48000) * 0.13
    )

    # Test case 7: Not eligible due to income being too high
    assert (
        calcietc(
            taxable_income=100000,
            is_wff_recipient=False,
            is_super_recipient=False,
            is_benefit_recipient=False,
            ietc_params=ietc_params,
        )
        == 0
    )


@pytest.fixture
def donation_credit_params() -> DonationCreditParams:
    """Returns a default set of donation credit parameters for testing."""
    return DonationCreditParams(
        credit_rate=1/3,
        min_donation=5.0,
    )


def test_calculate_donation_credit(donation_credit_params: DonationCreditParams):
    """Test the calculate_donation_credit function."""
    # Test case 1: Donation below minimum
    assert calculate_donation_credit(4.99, 50000, donation_credit_params) == 0.0

    # Test case 2: Donation above minimum
    assert calculate_donation_credit(100, 50000, donation_credit_params) == 100 * (1/3)

    # Test case 3: Donation exceeds taxable income
    assert calculate_donation_credit(60000, 50000, donation_credit_params) == 50000 * (1/3)

    # Test case 4: Zero donation
    assert calculate_donation_credit(0, 50000, donation_credit_params) == 0.0
