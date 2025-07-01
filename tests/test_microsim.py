"""
Unit tests for the microsimulation tax functions.

This module contains tests for the functions defined in `src/microsim.py`,
ensuring their correctness and adherence to the original SAS model logic.
"""

from src.microsim import (
    calcietc,
    calctax,
    eitc,
    family_boost_credit,
    load_parameters,
    netavg,
    simrwt,
    supstd,
    taxit,
)

# Load parameters for testing
params_2023_24 = load_parameters("2023-2024")
params_2024_25 = load_parameters("2024-2025")


def test_taxit():
    """
    Tests the taxit function with various income scenarios and tax brackets.
    """
    # Rates and thresholds for the 2023 tax year
    rates = params_2023_24["tax_brackets"]["rates"]
    thresholds = params_2023_24["tax_brackets"]["thresholds"]

    # Test case 1: Income within the first bracket
    assert taxit(10000, rates, thresholds) == 1050

    # Test case 2: Income in the second bracket
    assert taxit(20000, rates, thresholds) == 14000 * 0.105 + (20000 - 14000) * 0.175

    # Test case 3: Income in the third bracket
    assert taxit(60000, rates, thresholds) == (14000 * 0.105) + ((48000 - 14000) * 0.175) + ((60000 - 48000) * 0.30)

    # Test case 4: Income in the fourth bracket
    assert taxit(100000, rates, thresholds) == (14000 * 0.105) + ((48000 - 14000) * 0.175) + (
        (70000 - 48000) * 0.30
    ) + ((100000 - 70000) * 0.33)

    # Test case 5: Income in the fifth bracket
    assert taxit(200000, rates, thresholds) == (14000 * 0.105) + ((48000 - 14000) * 0.175) + (
        (70000 - 48000) * 0.30
    ) + ((180000 - 70000) * 0.33) + ((200000 - 180000) * 0.39)

    # Test case 6: Zero income
    assert taxit(0, rates, thresholds) == 0

    # Test case 7: Negative income
    assert taxit(-1000, rates, thresholds) == 0


def test_calctax():
    """
    Tests the calctax function for split-year tax calculations.
    """
    # Rates and thresholds for the 2023 tax year
    rates1 = params_2023_24["tax_brackets"]["rates"]
    thresholds1 = params_2023_24["tax_brackets"]["thresholds"]

    # Rates and thresholds for the 2024 tax year
    rates2 = params_2024_25["tax_brackets"]["rates"]
    thresholds2 = params_2024_25["tax_brackets"]["thresholds"]

    # Test case 1: Split year with same rates and thresholds
    assert calctax(60000, 6, rates1, thresholds1, rates1, thresholds1) == taxit(60000, rates1, thresholds1)

    # Test case 2: Split year with different rates and thresholds
    tax1 = taxit(60000, rates1, thresholds1)
    tax2 = taxit(60000, rates2, thresholds2)
    expected_tax = tax1 * 0.5 + tax2 * 0.5
    assert calctax(60000, 6, rates1, thresholds1, rates2, thresholds2) == expected_tax


def test_netavg():
    """
    Tests the netavg function for calculating net average income.
    """
    # Rates and thresholds for the 2023 tax year
    rates = params_2023_24["tax_brackets"]["rates"]
    thresholds = params_2023_24["tax_brackets"]["thresholds"]
    eprt = 0.0146

    # Test case 1
    incvar = 1000
    annearn = incvar * 52
    temptax = taxit(annearn, rates, thresholds)
    expected_net = int(100 * (annearn * (1 - eprt) - temptax) / 52) / 100
    assert netavg(incvar, eprt, rates, thresholds) == expected_net


def test_calcietc():
    """
    Tests the calcietc function, including various scenarios for IETC calculation and take-up logic.
    """
    ietc_params = params_2023_24["ietc"]
    # Test case 1: Eligible based on income, but did NOT claim before (ietc0=0).
    # Model assumes they "self-selected out". Should return 0.
    assert (
        calcietc(
            taxy=30000,
            parmflag="ys",
            wffamt=0,
            supamt=0,
            benamt=0,
            ietc_params=ietc_params,
            ietc0=0,
            taxinc0=30000,
        )
        == 0
    )

    # Test case 2: Eligible based on income, AND claimed before (ietc0 > 0).
    # Should receive the full credit.
    assert (
        calcietc(
            taxy=30000,
            parmflag="ys",
            wffamt=0,
            supamt=0,
            benamt=0,
            ietc_params=ietc_params,
            ietc0=1,
            taxinc0=30000,
        )
        == 520
    )

    # Test case 3: Eligible with abatement, AND claimed before (ietc0 > 0).
    # Should receive the abated credit.
    assert calcietc(
        taxy=50000,
        parmflag="ys",
        wffamt=0,
        supamt=0,
        benamt=0,
        ietc_params=params_2023_24["ietc"],
        ietc0=1,
        taxinc0=50000,
    ) == max(0, 520 - 0.13 * (50000 - 48000))

    # Test case 4: Not eligible (income too low), even if claimed before.
    assert (
        calcietc(
            taxy=20000,
            parmflag="ys",
            wffamt=0,
            supamt=0,
            benamt=0,
            ietc_params=ietc_params,
            ietc0=1,
            taxinc0=20000,
        )
        == 0
    )

    # Test case 5: Receiving WFF. The take-up logic is skipped.
    # If they claimed IETC before (ietc0 > 0), the model would give it to them.
    # This seems like a flaw in the original SAS, but for a faithful translation, we test that behaviour.
    assert (
        calcietc(
            taxy=30000,
            parmflag="ys",
            wffamt=100,
            supamt=0,
            benamt=0,
            ietc_params=ietc_params,
            ietc0=1,
            taxinc0=30000,
        )
        == 520
    )

    # Test case 6: Receiving WFF and did NOT claim IETC before.
    assert (
        calcietc(
            taxy=30000,
            parmflag="ys",
            wffamt=100,
            supamt=0,
            benamt=0,
            ietc_params=ietc_params,
            ietc0=0,
            taxinc0=30000,
        )
        == 0
    )


def test_eitc():
    """
    Tests the eitc function for Earned Income Tax Credit calculation.
    """
    # Test case 1: Earning zone
    assert eitc(1, 1, 10000, 5000, 15000, 20000, 0.1, 0.2) == 500

    # Test case 2: Stable zone
    assert eitc(1, 1, 18000, 5000, 15000, 20000, 0.1, 0.2) == 1000

    # Test case 3: Abatement zone
    assert eitc(1, 1, 22000, 5000, 15000, 20000, 0.1, 0.2) == max(0, 1000 - (22000 - 20000) * 0.2)

    # Test case 4: Not eligible
    assert eitc(1, 0, 10000, 5000, 15000, 20000, 0.1, 0.2) == 0

    # Test case 5: Credit not on
    assert eitc(0, 1, 10000, 5000, 15000, 20000, 0.1, 0.2) == 0


def test_simrwt():
    """
    Tests the simrwt function for Resident Withholding Tax simulation.
    """
    # Test case 1
    assert simrwt(1000, 0.1, 0.2, 0.3, 0.4, 0.5) == min(
        1000, 1000 * (0 + 1.05 * 0.1 + 1.75 * 0.2 + 0.30 * 0.3 + 0.33 * 0.4 + 0.39 * 0.5)
    )

    # Test case 2: Zero interest
    assert simrwt(0, 0.1, 0.2, 0.3, 0.4, 0.5) == 0

    # Test case 3: Negative interest
    assert simrwt(-1000, 0.1, 0.2, 0.3, 0.4, 0.5) == 0


def test_supstd():
    """
    Tests the supstd function for standard superannuation calculation.
    """
    # Base year parameters
    awe22 = 1462.81
    ep_base = 0.0153
    tax_params_base = params_2023_24["tax_brackets"]

    # Simulation year parameters
    cpi_factors = [1.05, 1.04, 1.03, 1.02]
    awe = [1546.57, 1630.11, 1701.45, 1763.49]
    ep = [0.016, 0.016, 0.016, 0.016]
    fl = [0.66, 0.66, 0.66, 0.66]
    tax_params = [
        params_2023_24["tax_brackets"],
        params_2023_24["tax_brackets"],
        params_2023_24["tax_brackets"],
        params_2023_24["tax_brackets"],
    ]

    # Expected results
    expected_std22 = awe22 * 0.66 * 2
    expected_stdnet22 = netavg(expected_std22 / 2, ep_base, tax_params_base["rates"], tax_params_base["thresholds"])

    expected_std = []
    expected_stdnet = []
    std_prev = expected_std22
    for i in range(4):
        std = max(awe[i] * fl[i] * 2, std_prev * cpi_factors[i])
        stdnet = netavg(std / 2, ep[i], tax_params[i]["rates"], tax_params[i]["thresholds"])
        expected_std.append(std)
        expected_stdnet.append(stdnet)
        std_prev = std

    # Run the function
    results = supstd(cpi_factors, awe, ep, fl, tax_params, awe22, ep_base, tax_params_base)

    # Assertions
    assert results["std22"] == expected_std22
    assert results["stdnet22"] == expected_stdnet22
    assert results["std"] == expected_std[0]
    assert results["stdnet"] == expected_stdnet[0]
    assert results["std1"] == expected_std[1]
    assert results["stdnet1"] == expected_stdnet[1]
    assert results["std2"] == expected_std[2]
    assert results["stdnet2"] == expected_stdnet[2]
    assert results["std3"] == expected_std[3]
    assert results["stdnet3"] == expected_stdnet[3]


def test_family_boost_credit():
    """
    Tests the family_boost_credit function with various scenarios.
    """
    family_boost_params = params_2024_25["family_boost"]

    # Test case 1: Income below threshold, credit is 25% of costs
    assert family_boost_credit(100000, 1000, family_boost_params) == 250

    # Test case 2: Income below threshold, credit is capped at max_credit
    assert family_boost_credit(100000, 20000, family_boost_params) == family_boost_params["max_credit"]

    # Test case 3: Income above threshold, credit is abated
    credit = min(10000 * 0.25, family_boost_params["max_credit"])
    abatement = (150000 - family_boost_params["income_threshold"]) * family_boost_params["abatement_rate"]
    expected_credit = max(0, credit - abatement)
    assert family_boost_credit(150000, 10000, family_boost_params) == expected_credit

    # Test case 4: Income above max_income, credit is 0
    assert family_boost_credit(190000, 10000, family_boost_params) == 0
