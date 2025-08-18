import yfinance as yf
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
from decimal import Decimal
import firebase_admin
from firebase_admin import credentials, firestore  # Updated import
import json  # Added for JSON parsing

from app.config.settings import settings
from app.services import nlp_integration 
from app.services.rate_limiter import rate_limiter
from app.schemas.financial import (
    StockDataRequest, StockDataResponse, StockPrice
)
from app.utils.logger import log_metadata

# Service account JSON (paste your provided JSON here)
service_account_json = {
  "type": "service_account",
  "project_id": "finguard-b3ed2",
  "private_key_id": "7b97b57fe3cbcc98b1904313eae68df2cfff4438",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCZcSBjJCLkd1hn\n50/wCT6nN09ysIq5MSEK5x5t7ORW0IFA/92OSFjw93DS7o3bmglRGxUp7ySllWZW\nz1edQMVAsVzl2lu87jSd+q49rFtPeYruk39fzgqLYDRT3R0Kg86SWLzkj3nXEi00\nLAboNGznhVtfP4W7vognuCw5V/NAQ/sl6B1uWDrPFcgyd1bsataZ0OyuqYXg7DU3\nbKz8QSWpcOOpfT/fzmnyz+stVUhq6+VDRpEypXDS+u7UIDO3WQKpH61A50F4CfbZ\n4juyBiqgq3TSJzfeR1T+/YEdvw4eAMftF6ZXZ6gEcuzJL8BEpKojgQp67I1eAlSZ\n55AAgiS5AgMBAAECggEANhkedBXPf4FcV/XDxztbLZVgm20G29gocDGgFt2Ie9sz\nVvle4cU8Jmj3DEczGJOsaT4FLi20W/Taigy8NSMa6H4f5KIh6fCJ+JDjUbcs0k5l\n30t9gwefzBf1GwRAMu7Zq9tBbcvwBxXPfi9vl/qz0sS/vEsnGVRJqMdUQDtz9dn1\n7B9S1FCEnMImKm9Ty0om8eK+Bh2ZlE1N4TBFEZ3Gj5bAHMjiyvmtNXR97bPltgD3\nI+t/ffyLRWfIOsZfu97Szg/6XyOZ6X92x6HMP3zeD69qcMkNHdM9HzhlrPc8RxIi\nCH4JTCusWj1QYhISpKSxerpQlflPmzk1/kprE3xM6QKBgQDTbZADD050LjP/JIkL\nqW4piskI2Gd73Xbla04KRtuch8O6VKf2HMocI5nboH9A6RHVJiFxsKeca0tyjIBl\nhBATzDREDm1ifZ3lvtm7B8lH/82QEaYU+K2ASb9f25/hqV+B9kwZJbS7i0dJtZct\nSevKbx0VzCCE04FyorzRcd6MTwKBgQC5yiVfADpncUbL/rxNI2lRV96+AKExMPZo\nE+88NBdKikX4srVttG5gNfbv8xnAwWVGD4Kjtmsw/B2B9+mcUXso0gfspxNgCm17\nXebjnJkMaeWPINs2dA44ZSTnQPWcuwYVV0BaRWMlfR5QDfZuQSC7BCReJ72XK8QI\nSJLaaWtUdwKBgHAMZIH6nq1bvxq8lhSkGknRz3Dsnws590TmdVlk7AYsvUIGk20P\nHN2E0IlgqZAQ9O5tYtQJtwpion12kKU8M/kKA7j9nGLSB9g2KNXB7p5Fpv9vGwGK\nOQkADHgUwMqrJH6PtQyuuvWZfpJFtnS99EQ4VsWyhJlgLf4+2Kp3GmZpAoGBAKHF\nCdU2daQsVeC55WulMcbKJAB8u94BLAxjjyN0l/MngtWRhbgIKzNKycEUg4/61Ruz\n1aSG6b61R1wraRXbPMnGV3AP6ibt7XZFxQzbBchxTJjbmwRG+TrRlthlD3dwwVND\nrZzsXe/+ia5a+f/2ZXFxodj58XL3gLFVv8i9kd7xAoGBAK/m2xk1qyRnTPqK4L8m\nngIOjZkD36TW70kobHw4vQjdCmz4iT+0lNF2w5asycJjB+l6mpYhJSfhjlxa+MhR\nUThls2nJpGfdO9Hq2owj655aKEgn9ofS8W+TJJ/n+N21cfb6CQOoKaGVmH9gazrz\nSUAKYIBF/4VvGyU6JTZzaStN\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@finguard-b3ed2.iam.gserviceaccount.com",
  "client_id": "103805546469447196721",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40finguard-b3ed2.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# Initialize Firebase with the JSON dict directly
if not firebase_admin._apps:
    cred = credentials.Certificate(service_account_json)
    firebase_admin.initialize_app(cred)

db = firestore.client()  # Firestore client

class FinancialService:
    def __init__(self):
        pass
    
    async def get_stock_data(self, request: StockDataRequest, user_id: str = "anonymous") -> StockDataResponse:
        """Fetch stock price data with rate limiting (no caching)"""
        start_time = datetime.utcnow()
        
        try:
            # Validate dates (prevent future/invalid ranges)
            today = datetime.utcnow().date()
            if request.end_date > today:
                request.end_date = today
            if request.start_date >= request.end_date:
                raise Exception("Start date must be before end date")
            
            # Check rate limits
            if not rate_limiter.can_make_request("yahoo_finance"):
                raise Exception("Rate limit exceeded for Yahoo Finance API")
            
            # Fetch real data from Yahoo Finance with fallback
            ticker = yf.Ticker(request.ticker)
            hist_data = ticker.history(
                start=request.start_date,
                end=request.end_date + timedelta(days=1)  # Include end date
            )
            
            if hist_data.empty:
                # Fallback: Try shorter period
                hist_data = ticker.history(period="1mo")
                if hist_data.empty:
                    raise Exception(f"No data found for ticker {request.ticker} - check symbol or dates")
            
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
            
            # NLP integration (as before)...
            
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

    
    async def get_user_portfolio_data(self, user_id: str) -> Dict[str, Any]:
        """Fetch user's portfolio from Firestore, enrich stock holdings with yfinance data"""
        try:
            # Fetch user data from Firestore
            user_doc = db.collection('users').document(user_id).get()
            if not user_doc.exists:
                raise Exception(f"No user found for ID: {user_id}")
            user_data = user_doc.to_dict()
            
            # Fetch portfolio (filter by userId field)
            portfolios_ref = db.collection('portfolios').where('userId', '==', user_id).stream()
            portfolios = [p.to_dict() for p in portfolios_ref]
            if not portfolios:
                raise Exception(f"No portfolio found for user: {user_id}")
            portfolio_data = portfolios[0]  # Assumes one portfolio; use loop if multiple
            
            # Fetch holdings (filter by userId)
            holdings_snap = db.collection('holdings').where('userId', '==', user_id).stream()
            holdings = [h.to_dict() for h in holdings_snap]
            
            enriched_holdings = []
            total_value = 0.0
            
            for holding in holdings:
                if holding['assetType'] != 'stock':
                    # Non-stock - keep as-is
                    enriched_holdings.append(holding)
                    total_value += holding['quantity'] * holding['currentPrice']
                    continue
                
                symbol = holding['symbol']
                
                # Rate limit check
                if not rate_limiter.can_make_request("yahoo_finance"):
                    raise Exception("Rate limit exceeded for Yahoo Finance API")
                
                # Fetch from yfinance with error handling
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info  # Current snapshot
                    hist = ticker.history(period="1d")  # Latest day for price
                    
                    if hist.empty:
                        log_metadata({"function": "get_user_portfolio_data", "status": "warning", "message": f"No data for {symbol} - using stored price"})
                        latest_close = holding['currentPrice']  # Fallback to stored value
                    else:
                        latest_close = hist['Close'][-1]
                    
                    current_value = holding['quantity'] * latest_close
                    
                    enriched_holding = {
                        **holding,
                        "currentPrice": latest_close,
                        "currentValue": current_value,
                        "marketCap": info.get('marketCap'),
                        "volume": info.get('volume'),
                        "fiftyTwoWeekHigh": info.get('fiftyTwoWeekHigh'),
                        "fiftyTwoWeekLow": info.get('fiftyTwoWeekLow'),
                        "dividendYield": info.get('dividendYield'),
                        "peRatio": info.get('trailingPE'),
                        "updatedAt": datetime.utcnow().isoformat()
                    }
                    
                    enriched_holdings.append(enriched_holding)
                    total_value += current_value
                except Exception as yf_err:
                    log_metadata({"function": "get_user_portfolio_data", "status": "error", "message": f"yfinance failed for {symbol}: {yf_err}"})
                    # Fallback: Use stored values without enrichment
                    enriched_holdings.append(holding)
                    total_value += holding['quantity'] * holding['currentPrice']
            
            response = {
                "user": user_data,
                "portfolio": {
                    **portfolio_data,
                    "totalValue": total_value,
                    "updatedAt": datetime.utcnow().isoformat()
                },
                "holdings": enriched_holdings
            }
            
            log_metadata({
                "function": "get_user_portfolio_data",
                "user_id": user_id,
                "status": "success",
                "total_value": total_value
            })
            
            return response
        
        except Exception as e:
            log_metadata({
                "function": "get_user_portfolio_data",
                "user_id": user_id,
                "status": "error",
                "error": str(e)
            })
            raise



# Global service instance
financial_service = FinancialService()
