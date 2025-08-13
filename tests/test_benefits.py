from src.benefits import (
    _apply_abatement,
    calculate_accommodation_supplement,
    calculate_child_support,
    calculate_disability_allowance,
    calculate_jss,
    calculate_ppl,
    calculate_slp,
    calculate_sps,
)
from src.parameters import (
    AccommodationSupplementParams,
    ChildSupportParams,
    DisabilityAllowanceParams,
    JSSParams,
    PPLParams,
    SLPParams,
    SPSParams,
)

# Dummy parameters for testing
jss_params = JSSParams(
    single_rate=336.89,
    couple_rate=280.74,
    child_rate=0.0,
    income_abatement_threshold=115.0,
    abatement_rate=0.70,
)

sps_params = SPSParams(base_rate=476.69, income_abatement_threshold=115.0, abatement_rate=0.70)

slp_params = SLPParams(
    single_rate=399.09,
    couple_rate=280.74,
    income_abatement_threshold=115.0,
    abatement_rate=0.70,
)

as_params = AccommodationSupplementParams(
    income_thresholds={"single_no_children": 250.0, "with_children": 400.0},
    abatement_rate=0.25,
    max_entitlement_rates={
        "Auckland": {"single_no_children": 140.0, "with_children": 200.0},
        "Wellington": {"single_no_children": 120.0, "with_children": 180.0},
        "Christchurch": {"single_no_children": 100.0, "with_children": 150.0},
    },
    housing_cost_contribution_rate=0.70,
    housing_cost_threshold=25.0,
)

ppl_params = PPLParams(enabled=True, weekly_rate=600.0, max_weeks=26)
child_support_params = ChildSupportParams(enabled=True, support_rate=0.18, living_allowance=17518.28)


def test_apply_abatement():
    assert _apply_abatement(100, 50, 100, 0.5) == 100
    assert _apply_abatement(100, 150, 100, 0.5) == 75
    assert _apply_abatement(100, 400, 100, 1.0) == 0


def test_calculate_jss():
    # Test case 1: Single, no children, income below threshold
    assert calculate_jss(100, True, False, 0, jss_params) == jss_params.single_rate

    # Test case 2: Partnered, no children, income below threshold
    assert calculate_jss(100, False, True, 0, jss_params) == jss_params.couple_rate

    # Test case 3: Single, with children, income below threshold
    assert calculate_jss(100, True, False, 1, jss_params) == jss_params.single_rate + jss_params.child_rate

    # Test case 4: Single, income above threshold, abated
    expected_jss = jss_params.single_rate - (200 - jss_params.income_abatement_threshold) * jss_params.abatement_rate
    assert calculate_jss(200, True, False, 0, jss_params) == max(0, expected_jss)

    # Test case 5: Single, income very high, abated to 0
    assert calculate_jss(1000, True, False, 0, jss_params) == 0.0


def test_calculate_sps():
    # Test case 1: Has children, income below threshold
    assert calculate_sps(100, 1, sps_params) == sps_params.base_rate

    # Test case 2: Has children, income above threshold, abated
    expected_sps = sps_params.base_rate - (200 - sps_params.income_abatement_threshold) * sps_params.abatement_rate
    assert calculate_sps(200, 1, sps_params) == max(0, expected_sps)

    # Test case 3: No children
    assert calculate_sps(100, 0, sps_params) == 0.0


def test_calculate_slp():
    # Test case 1: Disabled, single, income below threshold
    assert calculate_slp(100, True, False, True, slp_params) == slp_params.single_rate

    # Test case 2: Disabled, partnered, income below threshold
    assert calculate_slp(100, False, True, True, slp_params) == slp_params.couple_rate

    # Test case 3: Not disabled
    assert calculate_slp(100, True, False, False, slp_params) == 0.0

    # Test case 4: Disabled, single, income above threshold, abated
    expected_slp = slp_params.single_rate - (200 - slp_params.income_abatement_threshold) * slp_params.abatement_rate
    assert calculate_slp(200, True, False, True, slp_params) == max(0, expected_slp)


def test_calculate_accommodation_supplement():
    # Test case 1: Single, no children, Auckland, low income, high housing costs
    expected_as = min(
        (400 - as_params.housing_cost_threshold) * as_params.housing_cost_contribution_rate,
        as_params.max_entitlement_rates["Auckland"]["single_no_children"],
    )
    assert calculate_accommodation_supplement(100, 400, "Auckland", 0, as_params) == expected_as

    # Test case 2: With children, Wellington, low income, high housing costs
    expected_as = min(
        (500 - as_params.housing_cost_threshold) * as_params.housing_cost_contribution_rate,
        as_params.max_entitlement_rates["Wellington"]["with_children"],
    )
    assert calculate_accommodation_supplement(100, 500, "Wellington", 2, as_params) == expected_as

    # Test case 3: Single, no children, Christchurch, income above threshold, abated
    initial_entitlement = min(
        (300 - as_params.housing_cost_threshold) * as_params.housing_cost_contribution_rate,
        as_params.max_entitlement_rates["Christchurch"]["single_no_children"],
    )
    abatement = (300 - as_params.income_thresholds["single_no_children"]) * as_params.abatement_rate
    expected_as = max(0, initial_entitlement - abatement)
    assert calculate_accommodation_supplement(300, 300, "Christchurch", 0, as_params) == expected_as

    # Test case 4: Income very high, AS is 0
    assert calculate_accommodation_supplement(1000, 400, "Auckland", 0, as_params) == 0.0

    # Test case 5: Housing costs too low
    assert calculate_accommodation_supplement(100, 10, "Auckland", 0, as_params) == 0.0


def test_calculate_ppl():
    """PPL should pay the weekly rate up to the maximum weeks when enabled."""
    assert calculate_ppl(-10, ppl_params) == 0.0
    assert calculate_ppl(0, ppl_params) == 0.0
    assert calculate_ppl(10, ppl_params) == 600.0 * 10
    assert calculate_ppl(26, ppl_params) == 600.0 * 26
    assert calculate_ppl(30, ppl_params) == 600.0 * 26

    disabled = PPLParams(enabled=False, weekly_rate=600.0, max_weeks=26)
    assert calculate_ppl(10, disabled) == 0.0


def test_calculate_child_support():
    """Child support is a fixed share of liable income when enabled."""

    # Test case 1: Income above living allowance
    assert (
        calculate_child_support(50000, child_support_params) == (50000 - child_support_params.living_allowance) * 0.18
    )

    # Test case 2: Income below living allowance
    assert calculate_child_support(10000, child_support_params) == 0.0

    # Test case 3: Disabled
    disabled = ChildSupportParams(enabled=False, support_rate=0.18, living_allowance=17518.28)
    assert calculate_child_support(50000, disabled) == 0.0


disability_allowance_params = DisabilityAllowanceParams(
    max_payment=80.35,
    income_thresholds={
        "single_16_17": 675.60,
        "single_18_plus": 843.78,
        "couple": 1256.07,
        "sole_parent_1_child": 942.23,
        "sole_parent_2_plus_children": 992.74,
    },
)


def test_calculate_disability_allowance():
    # Test case 1: Eligible, costs below max
    assert calculate_disability_allowance(500, 50, "single_18_plus", disability_allowance_params) == 50

    # Test case 2: Eligible, costs above max
    assert calculate_disability_allowance(500, 100, "single_18_plus", disability_allowance_params) == 80.35

    # Test case 3: Ineligible, income too high
    assert calculate_disability_allowance(900, 50, "single_18_plus", disability_allowance_params) == 0

    # Test case 4: Invalid family situation
    assert calculate_disability_allowance(500, 50, "invalid_situation", disability_allowance_params) == 0
