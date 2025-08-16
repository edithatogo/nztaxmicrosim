import os
import shutil
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
from pathlib import Path
import pandas as pd
from typing import Optional, Dict, Any

from ..microsim import load_parameters
from ..dynamic_simulation import _run_static_simulation
from .tasks import run_optimisation_task
from .celery_app import celery_app

# Create a directory for uploads if it doesn't exist
UPLOAD_DIR = Path("data/api_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Load the default population dataset
DEFAULT_POPULATION_PATH = "src/data/default_population.csv"
if os.path.exists(DEFAULT_POPULATION_PATH):
    default_pop_df = pd.read_csv(DEFAULT_POPULATION_PATH)
else:
    default_pop_df = None

app = FastAPI(
    title="NZ Tax Microsimulation Model API",
    description="An API to run the NZ Tax Microsimulation Model.",
    version="0.1.0",
)

class StaticSimulationRequest(BaseModel):
    year: str = Field(..., description="The simulation year, e.g., '2023-2024'.")
    dataset_id: Optional[str] = Field(None, description="The ID of a previously uploaded dataset. If omitted, the default population is used.")
    parameter_overrides: Optional[Dict[str, Any]] = Field({}, description="A dictionary of policy parameters to override.")

class OptimisationRunRequest(BaseModel):
    year: str = Field(..., description="The base simulation year, e.g., '2023-2024'.")
    dataset_id: Optional[str] = Field(None, description="The ID of a previously uploaded dataset. If omitted, the default population is used.")
    optimisation_config: Dict[str, Any] = Field(..., description="The Optuna study configuration.")

@app.get("/")
def read_root():
    return {"message": "Welcome to the NZ Tax Microsimulation Model API"}

@app.post("/data/upload")
async def upload_data(file: UploadFile = File(...)):
    """
    Upload a population dataset in CSV format.
    """
    if file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV.")

    dataset_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{dataset_id}.csv"

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    return {"dataset_id": dataset_id, "filename": file.filename}

@app.get("/data/{dataset_id}")
async def get_data_metadata(dataset_id: str):
    """
    Get metadata for a previously uploaded dataset.
    """
    file_path = UPLOAD_DIR / f"{dataset_id}.csv"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Dataset not found.")

    stat_info = file_path.stat()
    return {
        "dataset_id": dataset_id,
        "size_bytes": stat_info.st_size,
        "created_at": stat_info.st_ctime,
    }

@app.post("/simulation/static")
async def run_static_simulation(request: StaticSimulationRequest):
    """
    Run a static simulation for a given year with optional parameter overrides.
    """
    if request.dataset_id:
        file_path = UPLOAD_DIR / f"{request.dataset_id}.csv"
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Dataset not found.")
        df = pd.read_csv(file_path)
    else:
        if default_pop_df is None:
            raise HTTPException(status_code=500, detail="Default population dataset not available.")
        df = default_pop_df.copy()

    # Load base parameters
    try:
        params = load_parameters(request.year)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # Apply parameter overrides
    if request.parameter_overrides:
        # A helper function to set nested attributes would be good here.
        # For now, we'll assume simple overrides.
        # This part will be improved when we add the optimisation endpoint.
        from ..optimisation import _set_nested_attr
        for path, value in request.parameter_overrides.items():
            try:
                _set_nested_attr(params, path, value)
            except (AttributeError, KeyError, IndexError):
                raise HTTPException(status_code=400, detail=f"Invalid parameter path: {path}")

    # Calculate taxable_income from income components
    income_cols = ["employment_income", "self_employment_income", "investment_income", "rental_property_income", "private_pensions_annuities"]
    df["taxable_income"] = df[income_cols].sum(axis=1)

    # Run the simulation
    result_df = _run_static_simulation(df, params)

    # Calculate and return summary results
    total_tax_liability = result_df["tax_liability"].sum()
    total_wff_paid = result_df[[col for col in ["FTCcalc", "IWTCcalc", "BSTCcalc", "MFTCcalc"] if col in result_df.columns]].sum().sum()

    return {
        "total_tax_liability": total_tax_liability,
        "total_wff_paid": total_wff_paid,
        "num_records": len(result_df),
    }

@app.post("/optimisation/run", status_code=202)
async def run_optimisation(request: OptimisationRunRequest):
    """
    Start a new policy optimisation job.
    """
    if request.dataset_id:
        dataset_path = str(UPLOAD_DIR / f"{request.dataset_id}.csv")
        if not os.path.exists(dataset_path):
            raise HTTPException(status_code=404, detail="Dataset not found.")
    else:
        if default_pop_df is None:
            raise HTTPException(status_code=500, detail="Default population dataset not available.")
        dataset_path = DEFAULT_POPULATION_PATH

    task = run_optimisation_task.delay(
        opt_config=request.optimisation_config,
        base_year=request.year,
        dataset_path=dataset_path
    )

    return {"job_id": task.id}

@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """
    Get the status and result of a background job.
    """
    task_result = celery_app.AsyncResult(job_id)

    response = {
        "job_id": job_id,
        "status": task_result.status,
        "result": None
    }

    if task_result.successful():
        response["result"] = task_result.get()
    elif task_result.failed():
        # You might want to log the full traceback here
        response["result"] = str(task_result.info)

    return response
