import pandas as pd
from pydantic import BaseModel, Field


class SimulationInputSchema(BaseModel):
    """
    Defines the schema for the input data of the simulation.

    This Pydantic model is used to validate the input DataFrame, ensuring that
    it contains all the required columns and that the data in each column is
    of the correct type and within the expected range.
    """

    person_id: int = Field(default=..., description="Unique identifier for each person.")
    household_id: int = Field(default=..., description="Unique identifier for each household.")
    familyinc: float = Field(default=..., ge=0, description="Family income, must be non-negative.")
    num_children: int = Field(default=..., ge=0, description="Number of children in the family, must be non-negative.")
    adults: int = Field(default=..., ge=0, description="Number of adults in the family, must be non-negative.")
    maxkiddays: int = Field(default=..., ge=0, le=366, description="Max days for child benefit eligibility.")
    maxkiddaysbstc: int = Field(default=..., ge=0, le=366, description="Max days for BSTC eligibility.")
    FTCwgt: int = Field(default=..., ge=0, le=1, description="Weight for Family Tax Credit.")
    IWTCwgt: int = Field(default=..., ge=0, le=1, description="Weight for In-Work Tax Credit.")
    iwtc_elig: int = Field(default=..., ge=0, le=1, description="Eligibility for In-Work Tax Credit.")
    BSTC0wgt: int = Field(default=..., ge=0, le=1, description="Weight for Best Start Tax Credit (0-1).")
    BSTC01wgt: int = Field(default=..., ge=0, le=1, description="Weight for Best Start Tax Credit (1-2).")
    BSTC1wgt: int = Field(default=..., ge=0, le=1, description="Weight for Best Start Tax Credit (2-3).")
    pplcnt: int = Field(default=..., ge=0, description="Total number of people in the household.")
    MFTC_total: float = Field(default=..., ge=0, description="Total Minimum Family Tax Credit.")
    MFTC_elig: int = Field(default=..., ge=0, le=1, description="Eligibility for Minimum Family Tax Credit.")
    sharedcare: int = Field(default=..., ge=0, le=1, description="Shared care indicator.")
    sharecareFTCwgt: int = Field(default=..., ge=0, le=1, description="Shared care weight for Family Tax Credit.")
    sharecareBSTC0wgt: int = Field(default=..., ge=0, le=1, description="Shared care weight for BSTC (0-1).")
    sharecareBSTC01wgt: int = Field(default=..., ge=0, le=1, description="Shared care weight for BSTC (1-2).")
    sharecareBSTC1wgt: int = Field(default=..., ge=0, le=1, description="Shared care weight for BSTC (2-3).")
    MFTCwgt: int = Field(default=..., ge=0, le=1, description="Weight for Minimum Family Tax Credit.")
    iwtc: float = Field(default=..., ge=0, description="In-Work Tax Credit amount.")
    selfempind: int = Field(default=..., ge=0, le=1, description="Self-employment indicator.")


def validate_input_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate the input DataFrame against the SimulationInputSchema.

    This function uses the Pydantic model `SimulationInputSchema` to validate
    the input DataFrame. It checks for the presence of required columns, correct
    data types, and value ranges.

    Args:
        df: The DataFrame to be validated.

    Returns:
        The validated DataFrame.

    Raises:
        ValueError: If the DataFrame does not conform to the schema.
    """
    try:
        # Pydantic can validate a list of records
        records = df.to_dict("records")
        validated_records = []
        for r in records:
            validated_records.append(SimulationInputSchema(**{str(k): v for k, v in r.items()}))
        return pd.DataFrame([r.model_dump() for r in validated_records])
    except Exception as e:
        raise ValueError(f"Data validation failed: {e}")
