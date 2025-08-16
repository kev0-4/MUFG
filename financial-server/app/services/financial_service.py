import yfinance as yf
from typing import List, Optional
from datetime import datetime, timedelta
import asyncio
import random
from decimal import Decimal

from app.config.settings import settings
from app.services import nlp_integration
from app.services.rate_limiter import rate_limiter
from app.schemas.financial import (
    StockDataRequest, StockDataResponse, StockPrice
)
from app.utils.logger import log_metadata

class FinancialService:
    def __init__(self):
        pass  # No Alpha Vantage URL needed
    
    async def get_stock_data(self, request: StockDataRequest, user_id: str = "anonymous") -> StockDataResponse:
        """Fetch stock price data with rate limiting (no caching)"""
        start_time = datetime.utcnow()
        
        try:
            # Use mock data if enabled for development
            if settings.mock_data_enabled:
                return await self._get_mock_stock_data(request, user_id)
            
            # Check rate limits
            if not rate_limiter.can_make_request("yahoo_finance"):
                raise Exception("Rate limit exceeded for Yahoo Finance API")
            
            # Fetch real data from Yahoo Finance
            ticker = yf.Ticker(request.ticker)
            hist_data = ticker.history(
                start=request.start_date,
                end=request.end_date + timedelta(days=1)  # Include end date
            )
            
            if hist_data.empty:
                raise Exception(f"No data found for ticker {request.ticker}")
            
            # Convert to our schema
            prices = []
            for date, row in hist_data.iterrows():
                prices.append(StockPrice(
                    date=date.date(),
                    open=row['Open'],
                    high=row['High'], 
                    low=row['Low'],
                    close=row['Close'],
                    volume=int(row['Volume'])
                ))
            
            response_data = {
                "ticker": request.ticker,
                "prices": [price.dict() for price in prices],
                "meta": {"source": "yahoo_finance"},
                "cache_hit": False,
                "last_updated": datetime.utcnow()
            }
            
            # Integrate with NLP: Enhance the stock data with sentiment/explanation
            nlp_result = await nlp_integration.enhance_nlp(
                simulation_data=response_data,  # Send your stock data to NLP
                user_id=user_id,
                ai_prompt="Explain recession impact on this stock"  # Customize as needed
            )
            if nlp_result:
                response_data["nlp_enhancement"] = nlp_result.get("eli5_response")  # Add ELI5 explanation
                response_data["sentiment"] = nlp_result.get("news_sentiment")  # Add sentiment details
            
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            log_metadata({
                "function": "get_stock_data",
                "user_id": user_id,
                "ticker": request.ticker,
                "status": "success",
                "duration_ms": duration_ms,
                "api_source": "yahoo_finance"
            })
            
            return StockDataResponse(**response_data)
            
        except Exception as e:
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            log_metadata({
                "function": "get_stock_data", 
                "user_id": user_id,
                "ticker": request.ticker,
                "status": "error",
                "error": str(e),
                "duration_ms": duration_ms
            })
            raise

    
    async def _get_mock_stock_data(self, request: StockDataRequest, user_id: str) -> StockDataResponse:
        """Generate mock stock data for development"""
        base_price = Decimal('100.00')
        prices = []
        current_date = request.start_date
        
        while current_date <= request.end_date:
            daily_change = Decimal(str(random.uniform(-0.05, 0.05)))
            base_price = base_price * (1 + daily_change)
            
            daily_volatility = base_price * Decimal('0.02')
            open_price = base_price + Decimal(str(random.uniform(-float(daily_volatility), float(daily_volatility))))
            close_price = base_price + Decimal(str(random.uniform(-float(daily_volatility), float(daily_volatility))))
            high_price = max(open_price, close_price) + Decimal(str(random.uniform(0, float(daily_volatility))))
            low_price = min(open_price, close_price) - Decimal(str(random.uniform(0, float(daily_volatility))))
            
            prices.append(StockPrice(
                date=current_date,
                open=round(open_price, 2),
                high=round(high_price, 2),
                low=round(low_price, 2), 
                close=round(close_price, 2),
                volume=random.randint(1000000, 10000000)
            ))
            
            current_date += timedelta(days=1)
        
        response_data = {
            "ticker": request.ticker,
            "prices": prices,
            "meta": {"source": "mock_data"},
            "cache_hit": False,
            "last_updated": datetime.utcnow()
        }
        
        log_metadata({
            "function": "get_mock_stock_data",
            "user_id": user_id, 
            "ticker": request.ticker,
            "status": "success (mock)"
        })
        
        return StockDataResponse(**response_data)

# Global service instance
financial_service = FinancialService()