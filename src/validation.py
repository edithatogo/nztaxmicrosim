import pandas as pd
from pydantic import BaseModel, Field


class SimulationInputSchema(BaseModel):
    person_id: int = Field(..., description="Unique identifier for each person.")
    household_id: int = Field(..., description="Unique identifier for each household.")
    familyinc: float = Field(..., ge=0, description="Family income, must be non-negative.")
    num_children: int = Field(..., ge=0, description="Number of children in the family, must be non-negative.")
    adults: int = Field(..., ge=0, description="Number of adults in the family, must be non-negative.")
    maxkiddays: int = Field(..., ge=0, le=366, description="Max days for child benefit eligibility.")
    maxkiddaysbstc: int = Field(..., ge=0, le=366, description="Max days for BSTC eligibility.")
    FTCwgt: int = Field(..., ge=0, le=1, description="Weight for Family Tax Credit.")
    IWTCwgt: int = Field(..., ge=0, le=1, description="Weight for In-Work Tax Credit.")
    iwtc_elig: int = Field(..., ge=0, le=1, description="Eligibility for In-Work Tax Credit.")
    BSTC0wgt: int = Field(..., ge=0, le=1, description="Weight for Best Start Tax Credit (0-1).")
    BSTC01wgt: int = Field(..., ge=0, le=1, description="Weight for Best Start Tax Credit (1-2).")
    BSTC1wgt: int = Field(..., ge=0, le=1, description="Weight for Best Start Tax Credit (2-3).")
    pplcnt: int = Field(..., ge=0, description="Total number of people in the household.")
    MFTC_total: float = Field(..., ge=0, description="Total Minimum Family Tax Credit.")
    MFTC_elig: int = Field(..., ge=0, le=1, description="Eligibility for Minimum Family Tax Credit.")
    sharedcare: int = Field(..., ge=0, le=1, description="Shared care indicator.")
    sharecareFTCwgt: int = Field(..., ge=0, le=1, description="Shared care weight for Family Tax Credit.")
    sharecareBSTC0wgt: int = Field(..., ge=0, le=1, description="Shared care weight for Best Start Tax Credit (0-1).")
    sharecareBSTC01wgt: int = Field(..., ge=0, le=1, description="Shared care weight for Best Start Tax Credit (1-2).")
    sharecareBSTC1wgt: int = Field(..., ge=0, le=1, description="Shared care weight for Best Start Tax Credit (2-3).")
    MFTCwgt: int = Field(..., ge=0, le=1, description="Weight for Minimum Family Tax Credit.")
    iwtc: float = Field(..., ge=0, description="In-Work Tax Credit amount.")
    selfempind: int = Field(..., ge=0, le=1, description="Self-employment indicator.")


def validate_input_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates the input DataFrame against the SimulationInputSchema.

    Args:
        df: The DataFrame to validate.

    Returns:
        The validated DataFrame.

    Raises:
        ValueError: If the DataFrame does not conform to the schema.
    """
    try:
        # Pydantic can validate a list of records
        records = df.to_dict("records")
        validated_records = [SimulationInputSchema(**r) for r in records]
        return pd.DataFrame([r.dict() for r in validated_records])
    except Exception as e:
        raise ValueError(f"Data validation failed: {e}")
