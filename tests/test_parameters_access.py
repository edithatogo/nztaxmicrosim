from src.microsim import load_parameters


def test_parameters_dict_style_access() -> None:
    params = load_parameters("2023-2024")
    assert params.tax_brackets.rates == params.tax_brackets.rates
