from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal

class StockDataRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10, description="Stock ticker symbol")
    start_date: date = Field(..., description="Start date for data retrieval")
    end_date: date = Field(..., description="End date for data retrieval")
    
    @validator('ticker')
    def validate_ticker(cls, v):
        return v.upper().strip()
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

class StockPrice(BaseModel):
    date: date
    open: Decimal = Field(..., ge=0)
    high: Decimal = Field(..., ge=0) 
    low: Decimal = Field(..., ge=0)
    close: Decimal = Field(..., ge=0)
    volume: int = Field(..., ge=0)

class StockDataResponse(BaseModel):
    ticker: str
    prices: List[StockPrice]
    meta: Dict[str, Any] = {}
    cache_hit: bool = False
    last_updated: datetime

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0"
    dependencies: Dict[str, str] = {}
