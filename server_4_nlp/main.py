from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, Any
from services.orchestrator import orchestrate_query, orchestrate_enhance
from utils.logger import log_metadata

app = FastAPI(title="FinGuard NLP Server",
              description="NLP Server for Australian superannuation queries")


class QueryRequest(BaseModel):
    query: str
    user_id: str


class EnhanceRequest(BaseModel):
    simulation_data: Dict[str, Any]
    user_id: str
    ai_prompt: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True  # Allow arbitrary types like 'Any'


@app.post("/nlp/query")
async def process_query(request: QueryRequest):
    """
    Process a user query to extract intent, entities, and sentiments.

    Args:
        request (QueryRequest): Contains query and user_id.

    Returns:
        Dict[str, Any]: Intent, entities, query sentiment, and news sentiment.
    """
    try:
        result = orchestrate_query(request.query, request.user_id)
        log_metadata({
            "service": "main",
            "endpoint": "/nlp/query",
            "user_id": request.user_id,
            "query": request.query[:50],
            "result": result,
            "status": "success"
        })
        return result
    except ValueError as ve:
        log_metadata({
            "service": "main",
            "endpoint": "/nlp/query",
            "user_id": request.user_id,
            "query": request.query[:50] if request.query else "",
            "error": str(ve),
            "status": "error"
        })
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        log_metadata({
            "service": "main",
            "endpoint": "/nlp/query",
            "user_id": request.user_id,
            "query": request.query[:50] if request.query else "",
            "error": str(e),
            "status": "error"
        })
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.post("/nlp/enhance")
async def enhance_response(request: EnhanceRequest):
    """
    Enhance simulation data with news sentiment and ELI5 explanation.

    Args:
        request (EnhanceRequest): Contains simulation_data, user_id, and optional ai_prompt.

    Returns:
        Dict[str, Any]: Simulation data, news sentiment, and ELI5 response.
    """
    try:
        result = orchestrate_enhance(
            request.simulation_data, request.user_id, request.ai_prompt)
        log_metadata({
            "service": "main",
            "endpoint": "/nlp/enhance",
            "user_id": request.user_id,
            "simulation_data": request.simulation_data,
            "ai_prompt": request.ai_prompt,
            "result": result,
            "status": "success"
        })
        return result
    except ValueError as ve:
        log_metadata({
            "service": "main",
            "endpoint": "/nlp/enhance",
            "user_id": request.user_id,
            "simulation_data": request.simulation_data,
            "error": str(ve),
            "status": "error"
        })
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        log_metadata({
            "service": "main",
            "endpoint": "/nlp/enhance",
            "user_id": request.user_id,
            "simulation_data": request.simulation_data,
            "error": str(e),
            "status": "error"
        })
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
