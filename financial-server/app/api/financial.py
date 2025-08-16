from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional
from datetime import datetime, date, timedelta
import uuid

from app.schemas.financial import (
    StockDataRequest, StockDataResponse, HealthResponse
)
from app.services.financial_service import financial_service
from app.utils.logger import log_metadata

router = APIRouter(prefix="/api", tags=["financial"])

def get_user_id() -> str:
    """Simple user ID generation for tracking (in production, use proper auth)"""
    return str(uuid.uuid4())

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        dependencies={
            "yahoo_finance": "operational",
            "rate_limiter": "operational"
        }
    )

@router.post("/stock/data", response_model=StockDataResponse)
async def get_stock_data(
    request: StockDataRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_user_id)
):
    """
    Fetch historical stock price data
    
    - **ticker**: Stock symbol (e.g., AAPL, GOOGL, CBA.AX)
    - **start_date**: Start date for data retrieval
    - **end_date**: End date for data retrieval
    """
    try:
        # Validate date range
        if request.end_date > date.today():
            raise HTTPException(
                status_code=400,
                detail="End date cannot be in the future"
            )
        
        if (request.end_date - request.start_date).days > 365:
            raise HTTPException(
                status_code=400,
                detail="Date range cannot exceed 365 days"
            )
        
        result = await financial_service.get_stock_data(request, user_id)
        
        # Log successful request in background
        background_tasks.add_task(
            log_metadata,
            {
                "function": "api_stock_data",
                "user_id": user_id,
                "ticker": request.ticker,
                "status": "success",
                "cache_hit": result.cache_hit
            }
        )
        
        return result
        
    except Exception as e:
        log_metadata({
            "function": "api_stock_data",
            "user_id": user_id,
            "ticker": request.ticker,
            "status": "error", 
            "error": str(e)
        })
        
        if "rate limit" in str(e).lower():
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        elif "no data found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"No data found for ticker {request.ticker}")
        else:
            raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/stock/latest/{ticker}")
async def get_latest_stock_price(
    ticker: str,
    user_id: str = Depends(get_user_id)
):
    """Get the latest stock price for a ticker"""
    try:
        # Get last 5 days of data to ensure we have recent data
        end_date = date.today()
        start_date = end_date - timedelta(days=5)
        
        request = StockDataRequest(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date
        )
        
        result = await financial_service.get_stock_data(request, user_id)
        
        if not result.prices:
            raise HTTPException(status_code=404, detail=f"No recent data found for {ticker}")
        
        # Return the most recent price
        latest_price = max(result.prices, key=lambda x: x.date)
        
        return {
            "ticker": result.ticker,
            "latest_price": latest_price,
            "as_of_date": latest_price.date,
            "cache_hit": result.cache_hit
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_metadata({
            "function": "api_latest_stock",
            "user_id": user_id,
            "ticker": ticker,
            "status": "error",
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail="Failed to fetch latest stock price")
