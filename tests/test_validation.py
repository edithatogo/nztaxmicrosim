import pandas as pd
import pytest

from src.validation import validate_input_data


@pytest.fixture
def valid_input_data():
    """A sample dataframe that is valid."""
    data = {
        "person_id": [1],
        "household_id": [1],
        "familyinc": [70000],
        "num_children": [2],
        "adults": [2],
        "maxkiddays": [365],
        "maxkiddaysbstc": [365],
        "FTCwgt": [1],
        "IWTCwgt": [1],
        "iwtc_elig": [1],
        "BSTC0wgt": [0],
        "BSTC01wgt": [0],
        "BSTC1wgt": [1],
        "pplcnt": [4],
        "MFTC_total": [0],
        "MFTC_elig": [0],
        "sharedcare": [0],
        "sharecareFTCwgt": [0],
        "sharecareBSTC0wgt": [0],
        "sharecareBSTC01wgt": [0],
        "sharecareBSTC1wgt": [0],
        "MFTCwgt": [0],
        "iwtc": [1],
        "selfempind": [0],
    }
    return pd.DataFrame(data)


def test_validate_input_data_valid(valid_input_data):
    """Test that valid data passes validation."""
    validated_df = validate_input_data(valid_input_data)
    assert isinstance(validated_df, pd.DataFrame)
    assert not validated_df.empty


def test_validate_input_data_invalid_missing_column(valid_input_data):
    """Test that data with a missing column fails validation."""
    invalid_data = valid_input_data.drop(columns=["familyinc"])
    with pytest.raises(ValueError):
        validate_input_data(invalid_data)


def test_validate_input_data_invalid_value(valid_input_data):
    """Test that data with an invalid value fails validation."""
    invalid_data = valid_input_data.copy()
    invalid_data["familyinc"] = -100
    with pytest.raises(ValueError):
        validate_input_data(invalid_data)


def test_validate_input_data_invalid_type(valid_input_data):
    """Test that data with an invalid type fails validation."""
    invalid_data = valid_input_data.copy()
    invalid_data["familyinc"] = "invalid"
    with pytest.raises(ValueError):
        validate_input_data(invalid_data)
