"""
Dashboard API endpoints for policy comparison and visualization.
Extends the existing FastAPI app with researcher-friendly endpoints.
"""

from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
from src.microsim import load_parameters
from src.simulation import run_simulation
from src.reporting import (
    calculate_gini_coefficient, 
    calculate_poverty_rate,
    calculate_total_tax_revenue,
    calculate_total_welfare_transfers
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class PolicyScenario(BaseModel):
    """Definition of a policy scenario for comparison."""
    name: str
    description: str
    base_year: str
    parameter_overrides: Dict[str, float]


class ComparisonRequest(BaseModel):
    """Request model for policy comparison."""
    scenarios: List[PolicyScenario]
    dataset_id: Optional[str] = None
    metrics: List[str] = ["gini", "poverty_rate", "tax_revenue", "welfare_transfers"]


class ComparisonResult(BaseModel):
    """Results of policy comparison analysis."""
    scenario_results: Dict[str, Dict[str, float]]
    distributional_data: Dict[str, List[float]]
    summary_stats: Dict[str, Dict[str, float]]


@router.post("/compare-policies", response_model=ComparisonResult)
async def compare_policies(request: ComparisonRequest):
    """
    Compare multiple policy scenarios and return key metrics.
    
    This endpoint is designed for researchers to quickly evaluate
    the distributional and fiscal impacts of different policy options.
    """
    results = {}
    distributional_data = {}
    summary_stats = {}
    
    # Load default population if no dataset specified
    if request.dataset_id is None:
        df = pd.read_csv("src/data/default_population.csv")
    else:
        # In a full implementation, load from dataset store
        df = pd.read_csv("src/data/default_population.csv")
    
    for scenario in request.scenarios:
        try:
            # Run simulation for this scenario
            scenario_df = run_simulation(
                df=df.copy(),
                year=scenario.base_year,
                mode="static",
                parameter_overrides=scenario.parameter_overrides
            )
            
            # Calculate requested metrics
            scenario_metrics = {}
            
            if "gini" in request.metrics:
                scenario_metrics["gini_coefficient"] = calculate_gini_coefficient(
                    scenario_df["disposable_income"]
                )
            
            if "poverty_rate" in request.metrics:
                scenario_metrics["poverty_rate"] = calculate_poverty_rate(
                    scenario_df, threshold=0.6
                )
            
            if "tax_revenue" in request.metrics:
                scenario_metrics["total_tax_revenue"] = calculate_total_tax_revenue(scenario_df)
            
            if "welfare_transfers" in request.metrics:
                scenario_metrics["total_welfare_transfers"] = calculate_total_welfare_transfers(scenario_df)
            
            # Store results
            results[scenario.name] = scenario_metrics
            
            # Store income distribution for charts
            distributional_data[scenario.name] = scenario_df["disposable_income"].tolist()
            
            # Calculate summary statistics
            summary_stats[scenario.name] = {
                "mean_income": float(scenario_df["disposable_income"].mean()),
                "median_income": float(scenario_df["disposable_income"].median()),
                "affected_individuals": len(scenario_df),
                "winners": len(scenario_df[scenario_df["net_benefit"] > 0]) if "net_benefit" in scenario_df else 0,
                "losers": len(scenario_df[scenario_df["net_benefit"] < 0]) if "net_benefit" in scenario_df else 0
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=400, 
                detail=f"Error processing scenario '{scenario.name}': {str(e)}"
            )
    
    return ComparisonResult(
        scenario_results=results,
        distributional_data=distributional_data,
        summary_stats=summary_stats
    )


@router.get("/available-parameters/{year}")
async def get_available_parameters(year: str):
    """
    Get all available parameters for a given tax year.
    Useful for building parameter override interfaces.
    """
    try:
        params = load_parameters(year)
        
        # Extract modifiable parameters with their current values
        available_params = {}
        
        if params.tax_brackets:
            available_params["tax_brackets"] = {
                "rates": params.tax_brackets.rates,
                "thresholds": params.tax_brackets.thresholds
            }
        
        if params.wff:
            available_params["wff"] = {
                "ftc1": params.wff.ftc1,
                "ftc2": params.wff.ftc2,
                "iwtc1": params.wff.iwtc1,
                "iwtc2": params.wff.iwtc2,
                "bstc": params.wff.bstc,
                "abatethresh1": params.wff.abatethresh1,
                "abatethresh2": params.wff.abatethresh2
            }
        
        if params.ietc:
            available_params["ietc"] = {
                "ent": params.ietc.ent,
                "thresh": params.ietc.thresh,
                "abate": params.ietc.abate
            }
        
        return available_params
        
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Parameters not found for year {year}: {str(e)}"
        )


@router.get("/policy-templates")
async def get_policy_templates():
    """
    Get predefined policy scenario templates for common research questions.
    """
    templates = {
        "higher_top_rate": {
            "name": "Higher Top Tax Rate",
            "description": "Increase top marginal tax rate from 39% to 45%",
            "parameter_overrides": {
                "tax_brackets.rates[4]": 0.45
            }
        },
        "increase_wff": {
            "name": "Increased Working for Families",
            "description": "Increase WFF credits by 20%",
            "parameter_overrides": {
                "wff.ftc1": 7970.4,  # 6642 * 1.2
                "wff.ftc2": 6494.4,  # 5412 * 1.2
                "wff.iwtc1": 6084.0  # 5070 * 1.2
            }
        },
        "lower_tax_thresholds": {
            "name": "Lower Tax Thresholds", 
            "description": "Reduce income tax thresholds by $5,000",
            "parameter_overrides": {
                "tax_brackets.thresholds[1]": 9500,   # 14000 - 5000
                "tax_brackets.thresholds[2]": 43000,  # 48000 - 5000
                "tax_brackets.thresholds[3]": 65000   # 70000 - 5000
            }
        },
        "enhanced_ietc": {
            "name": "Enhanced IETC",
            "description": "Increase IETC entitlement and raise threshold",
            "parameter_overrides": {
                "ietc.ent": 624.0,    # Increase from 520
                "ietc.thresh": 27000   # Increase threshold
            }
        }
    }
    
    return templates


@router.get("/health")
async def dashboard_health():
    """Health check endpoint for the dashboard API."""
    return {
        "status": "healthy",
        "endpoints": [
            "/dashboard/compare-policies",
            "/dashboard/available-parameters/{year}",
            "/dashboard/policy-templates",
            "/dashboard/health"
        ]
    }