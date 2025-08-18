from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, Any
from services.analytics_service import simulate_superannuation, recommend_strategy, calibrate_risk, scenario_simulation
from utils.logger import log_metadata

app = FastAPI(title="FinGuard AI Analytics Server", description="Analytics for superannuation planning")

class SimulateRequest(BaseModel):
    simulation_data: Dict[str, Any]
    user_id: str

    class Config:
        arbitrary_types_allowed = True

class RecommendRequest(BaseModel):
    user_id: str
    scenario: Optional[str] = None

class RiskRequest(BaseModel):
    user_id: str
    scenario: str
    economic_conditions: Dict[str, Any]

    class Config:
        arbitrary_types_allowed = True

class ScenarioRequest(BaseModel):
    user_id: str
    scenario: str
    monte_carlo_params: Dict[str, Any]
    economic_conditions: Dict[str, Any]

    class Config:
        arbitrary_types_allowed = True

@app.post("/analytics/simulate")
async def simulate_endpoint(request: SimulateRequest):
    """
    Simulate superannuation projections with Prophet forecasting.
    """
    try:
        result = simulate_superannuation(request.simulation_data, request.user_id)
        log_metadata({
            "service": "main",
            "endpoint": "/analytics/simulate",
            "user_id": request.user_id,
            "simulation_data": request.simulation_data,
            "result": result,
            "status": "success"
        })
        return result
    except ValueError as ve:
        log_metadata({
            "service": "main",
            "endpoint": "/analytics/simulate",
            "user_id": request.user_id,
            "simulation_data": request.simulation_data,
            "error": str(ve),
            "status": "error"
        })
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        log_metadata({
            "service": "main",
            "endpoint": "/analytics/simulate",
            "user_id": request.user_id,
            "simulation_data": request.simulation_data,
            "error": str(e),
            "status": "error"
        })
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/analytics/recommend")
async def recommend_endpoint(request: RecommendRequest):
    """
    Generate personalized strategy recommendations.
    """
    try:
        result = recommend_strategy(request.user_id, request.scenario)
        log_metadata({
            "service": "main",
            "endpoint": "/analytics/recommend",
            "user_id": request.user_id,
            "scenario": request.scenario,
            "result": result,
            "status": "success"
        })
        return result
    except ValueError as ve:
        log_metadata({
            "service": "main",
            "endpoint": "/analytics/recommend",
            "user_id": request.user_id,
            "scenario": request.scenario,
            "error": str(ve),
            "status": "error"
        })
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        log_metadata({
            "service": "main",
            "endpoint": "/analytics/recommend",
            "user_id": request.user_id,
            "scenario": request.scenario,
            "error": str(e),
            "status": "error"
        })
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/analytics/risk")
async def risk_endpoint(request: RiskRequest):
    """
    Calibrate risk based on scenario and economic conditions.
    """
    try:
        result = calibrate_risk(request.user_id, request.scenario, request.economic_conditions)
        log_metadata({
            "service": "main",
            "endpoint": "/analytics/risk",
            "user_id": request.user_id,
            "scenario": request.scenario,
            "result": result,
            "status": "success"
        })
        return result
    except ValueError as ve:
        log_metadata({
            "service": "main",
            "endpoint": "/analytics/risk",
            "user_id": request.user_id,
            "scenario": request.scenario,
            "error": str(ve),
            "status": "error"
        })
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        log_metadata({
            "service": "main",
            "endpoint": "/analytics/risk",
            "user_id": request.user_id,
            "scenario": request.scenario,
            "error": str(e),
            "status": "error"
        })
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/analytics/scenario")
async def scenario_endpoint(request: ScenarioRequest):
    """
    Run Monte Carlo scenario simulation with news sentiment.
    """
    try:
        result = scenario_simulation(request.user_id, request.scenario, request.monte_carlo_params, request.economic_conditions)
        log_metadata({
            "service": "main",
            "endpoint": "/analytics/scenario",
            "user_id": request.user_id,
            "scenario": request.scenario,
            "result": result,
            "status": "success"
        })
        return result
    except ValueError as ve:
        log_metadata({
            "service": "main",
            "endpoint": "/analytics/scenario",
            "user_id": request.user_id,
            "scenario": request.scenario,
            "error": str(ve),
            "status": "error"
        })
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        log_metadata({
            "service": "main",
            "endpoint": "/analytics/scenario",
            "user_id": request.user_id,
            "scenario": request.scenario,
            "error": str(e),
            "status": "error"
        })
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)