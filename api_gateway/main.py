import os
from fastapi import FastAPI, HTTPException, Request
import httpx
from utils.logger import log_metadata
from utils.test_module import run_all_tests
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="FinGuard API Gateway",
    description="Public API Gateway for FinGuard servers without encryption for development."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FINANCIAL_SERVER_URL = os.getenv("FINANCIAL_SERVER_URL", "http://20.244.41.104:8001")
NLP_SERVER_URL = os.getenv("NLP_SERVER_URL", "http://20.244.41.104:8000")
ANALYTICS_SERVER_URL = os.getenv("ANALYTICS_SERVER_URL", "http://20.244.41.104:8002")


@app.get("/")
async def hello_server():
    return {"Msg": "Welcome"}


@app.post("/api/user-data")
async def get_user_data(request: Request):
    try:
        body = await request.json()
        user_id = body.get("user_id")
        if not user_id:
            raise ValueError("Invalid request: user_id required")

        analytics_url = ANALYTICS_SERVER_URL + "/analytics/user-data"
        async with httpx.AsyncClient() as client:
            analytics_response = await client.post(analytics_url, json={"user_id": user_id})
        analytics_response.raise_for_status()
        response_data = analytics_response.json()

        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/user-data",
            "user_id": user_id,
            "status": "success"
        })
        return response_data
    except ValueError as ve:
        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/user-data",
            "error": str(ve),
            "status": "error"
        })
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/user-data",
            "error": str(e),
            "status": "error"
        })
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.post("/api/simulate")
async def simulate_investment(request: Request):
    try:
        body = await request.json()
        user_id = body.get("user_id")
        simulation_data = body.get("simulation_data")
        if not user_id or not simulation_data:
            raise ValueError("Invalid request: user_id and simulation_data required")

        analytics_url = ANALYTICS_SERVER_URL + "/analytics/simulate"
        async with httpx.AsyncClient() as client:
            analytics_response = await client.post(analytics_url, json={"user_id": user_id, "simulation_data": simulation_data})
        analytics_response.raise_for_status()
        response_data = analytics_response.json()

        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/simulate",
            "user_id": user_id,
            "status": "success"
        })
        return response_data
    except ValueError as ve:
        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/simulate",
            "error": str(ve),
            "status": "error"
        })
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/simulate",
            "error": str(e),
            "status": "error"
        })
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.post("/api/recommend")
async def get_recommendations(request: Request):
    try:
        body = await request.json()
        user_id = body.get("user_id")
        if not user_id:
            raise ValueError("Invalid request: user_id required")

        analytics_url = ANALYTICS_SERVER_URL + "/analytics/recommend"
        async with httpx.AsyncClient() as client:
            analytics_response = await client.post(analytics_url, json={"user_id": user_id})
        analytics_response.raise_for_status()
        response_data = analytics_response.json()

        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/recommend",
            "user_id": user_id,
            "status": "success"
        })
        return response_data
    except ValueError as ve:
        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/recommend",
            "error": str(ve),
            "status": "error"
        })
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/recommend",
            "error": str(e),
            "status": "error"
        })
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.post("/api/stock-sentiments")
async def analyze_stock_sentiments(request: Request):
    try:
        body = await request.json()
        user_id = body.get("user_id")
        if not user_id:
            raise ValueError("Invalid request: user_id required")

        nlp_url = NLP_SERVER_URL + "/nlp/user-stock-sentiments"
        async with httpx.AsyncClient() as client:
            nlp_response = await client.post(nlp_url, json={"userId": user_id}, headers={"Content-Type": "application/json"})
        nlp_response.raise_for_status()
        response_data = nlp_response.json()

        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/stock-sentiments",
            "user_id": user_id,
            "status": "success"
        })
        return response_data
    except ValueError as ve:
        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/stock-sentiments",
            "error": str(ve),
            "status": "error"
        })
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/stock-sentiments",
            "error": str(e),
            "status": "error"
        })
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.post("/api/enhance")
async def enhance_simulation(request: Request):
    try:
        body = await request.json()
        simulation_data = body.get("simulation_data")
        user_id = body.get("user_id")
        ai_prompt = body.get("ai_prompt")
        if not simulation_data or not user_id or not ai_prompt:
            raise ValueError("Invalid request: simulation_data, user_id, and ai_prompt required")

        nlp_url = NLP_SERVER_URL + "/nlp/enhance"
        async with httpx.AsyncClient() as client:
            nlp_response = await client.post(nlp_url, json={"simulation_data": simulation_data, "user_id": user_id, "ai_prompt": ai_prompt})
        nlp_response.raise_for_status()
        response_data = nlp_response.json()

        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/enhance",
            "user_id": user_id,
            "status": "success"
        })
        return response_data
    except ValueError as ve:
        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/enhance",
            "error": str(ve),
            "status": "error"
        })
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/enhance",
            "error": str(e),
            "status": "error"
        })
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.post("/api/query")
async def process_query(request: Request):
    try:
        body = await request.json()
        query = body.get("query")
        user_id = body.get("user_id")
        if not query or not user_id:
            raise ValueError("Invalid request: query and user_id required")

        nlp_url = NLP_SERVER_URL + "/nlp/query"
        async with httpx.AsyncClient() as client:
            nlp_response = await client.post(nlp_url, json={"query": query, "user_id": user_id})
        nlp_response.raise_for_status()
        response_data = nlp_response.json()

        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/query",
            "user_id": user_id,
            "query_length": len(query),
            "status": "success"
        })
        return response_data
    except ValueError as ve:
        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/query",
            "error": str(ve),
            "status": "error"
        })
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/query",
            "error": str(e),
            "status": "error"
        })
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.get("/api/stock-latest/{ticker}")
async def get_stock_latest(ticker: str):
    try:
        financial_url = FINANCIAL_SERVER_URL + f"/api/stock/latest/{ticker}"
        async with httpx.AsyncClient() as client:
            financial_response = await client.get(financial_url)
        financial_response.raise_for_status()
        response_data = financial_response.json()

        log_metadata({
            "service": "api_gateway",
            "endpoint": f"/api/stock-latest/{ticker}",
            "ticker": ticker,
            "status": "success"
        })
        return response_data
    except ValueError as ve:
        log_metadata({
            "service": "api_gateway",
            "endpoint": f"/api/stock-latest/{ticker}",
            "error": str(ve),
            "status": "error"
        })
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        log_metadata({
            "service": "api_gateway",
            "endpoint": f"/api/stock-latest/{ticker}",
            "error": str(e),
            "status": "error"
        })
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.post("/api/stock-data")
async def get_stock_data(request: Request):
    try:
        body = await request.json()
        ticker = body.get("ticker")
        start_date = body.get("start_date")
        end_date = body.get("end_date")
        if not ticker or not start_date or not end_date:
            raise ValueError("Invalid request: ticker, start_date, and end_date required")

        financial_url = FINANCIAL_SERVER_URL + "/api/stock/data"
        async with httpx.AsyncClient() as client:
            financial_response = await client.post(financial_url, json={"ticker": ticker, "start_date": start_date, "end_date": end_date})
        financial_response.raise_for_status()
        response_data = financial_response.json()

        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/stock-data",
            "ticker": ticker,
            "status": "success"
        })
        return response_data
    except ValueError as ve:
        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/stock-data",
            "error": str(ve),
            "status": "error"
        })
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        log_metadata({
            "service": "api_gateway",
            "endpoint": "/api/stock-data",
            "error": str(e),
            "status": "error"
        })
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.get("/api/public-key")
async def get_public_key():
    with open("keys/gateway_public_key.pem", "r") as f:
        return {"public_key": f.read()}


@app.get("/api/public-private-key")
async def get_public_private_key():
    with open("keys/client_private_key.pem", "r") as f:
        return {"private_key": f.read()}


@app.get("/api/test")
async def test():
    test_results = run_all_tests()
    success_count = sum(1 for result in test_results if result["status"] == "success")
    failure_count = len(test_results) - success_count
    return {
        "total_tests": len(test_results),
        "successful_tests": success_count,
        "failed_tests": failure_count,
        "results": test_results
    }








@app.get("/api/alpha-vantage")
async def alpha_vantage_service():
    from datetime import datetime
    import aiohttp
    import asyncio
    import redis
    import json
    from typing import Dict, Any
    async def make_async_api_call(session, url, params):
        """Make asynchronous API call"""
        async with session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.json()
    # Redis connection
    redis_conn = redis.Redis(
        host='redis-11788.c62.us-east-1-4.ec2.redns.redis-cloud.com',
        port=11788,
        decode_responses=True,
        username="default",
        password="h2n9cGmitI95GmERYQ73TmneBm0HMwrV",
    )
    
    # Alpha Vantage API Key (replace with your actual key)
    API_KEY = "LN6TK2B6L0R5M4D2"
    
    # Check cache first
    cache_key = "alpha_vantage_currencies_data"
    cached_data = redis_conn.get(cache_key)
    
    if cached_data:
        return json.loads(cached_data)
    
    # If not cached, fetch from API asynchronously
    base_url = "https://www.alphavantage.co/query"
    
    # Rare currencies to fetch
    rare_currencies = {
        'USDTRY': ('USD', 'TRY'),  # US Dollar to Turkish Lira
        'USDZAR': ('USD', 'ZAR'),  # US Dollar to South African Rand
        'USDRUB': ('USD', 'RUB'),  # US Dollar to Russian Ruble
        'USDHUF': ('USD', 'HUF'),  # US Dollar to Hungarian Forint
        'USDTHB': ('USD', 'THB'),  # US Dollar to Thai Baht
    }
    
    currencies_data = {}
    
    # Create all API tasks
    tasks = []
    async with aiohttp.ClientSession() as session:
        for name, (from_curr, to_curr) in rare_currencies.items():
            params = {
                'function': 'FX_DAILY',
                'from_symbol': from_curr,
                'to_symbol': to_curr,
                'apikey': API_KEY,
                'outputsize': 'compact'
            }
            tasks.append((name, from_curr, to_curr, make_async_api_call(session, base_url, params)))
        
        # Execute all API calls with rate limiting
        for i, (name, from_curr, to_curr, task) in enumerate(tasks):
            try:
                # Add delay between requests for rate limiting
                if i > 0:
                    await asyncio.sleep(1.2)  # Slightly more than 1 second for safety
                
                data = await task
                
                if 'Time Series FX (Daily)' in data:
                    time_series = data['Time Series FX (Daily)']
                    dates = sorted(time_series.keys(), reverse=True)[:7]
                    
                    last_7_days = {}
                    for date in dates:
                        daily_data = time_series[date]
                        last_7_days[date] = {
                            'open': float(daily_data.get('1. open', 0)),
                            'high': float(daily_data.get('2. high', 0)),
                            'low': float(daily_data.get('3. low', 0)),
                            'close': float(daily_data.get('4. close', 0))
                        }
                    
                    # Calculate performance
                    if len(dates) >= 2:
                        start_price = float(time_series[dates[-1]]['4. close'])
                        end_price = float(time_series[dates[0]]['4. close'])
                        price_change = end_price - start_price
                        percent_change = (price_change / start_price) * 100
                        
                        performance = {
                            'price_change': round(price_change, 4),
                            'percent_change': round(percent_change, 2),
                            'start_price': round(start_price, 4),
                            'end_price': round(end_price, 4)
                        }
                    else:
                        performance = {"error": "Insufficient data"}
                    
                    currencies_data[name] = {
                        'pair': f"{from_curr}/{to_curr}",
                        'metadata': {k: v for k, v in data.items() if k != 'Time Series FX (Daily)'},
                        'time_series': last_7_days,
                        'latest_rate': end_price if len(dates) > 0 else 0,
                        'performance_7d': performance
                    }
                else:
                    currencies_data[name] = {
                        'pair': f"{from_curr}/{to_curr}",
                        'error': "No time series data found",
                        'time_series': {},
                        'latest_rate': 0,
                        'performance_7d': {"error": "Data unavailable"}
                    }
                    
            except Exception as e:
                currencies_data[name] = {
                    'pair': f"{from_curr}/{to_curr}",
                    'error': str(e),
                    'time_series': {},
                    'latest_rate': 0,
                    'performance_7d': {"error": "Data unavailable"}
                }
    
    # Prepare final response
    result = {
        'metadata': {
            'data_source': 'Alpha Vantage',
            'timestamp': datetime.now().isoformat(),
            'time_period': 'last_7_trading_days',
            'currencies_count': len(currencies_data)
        },
        'currencies': currencies_data,
        'cache_status': 'miss'
    }
    
    # Cache the result for 1 hour (3600 seconds)
    redis_conn.setex(cache_key, 3600, json.dumps(result))
    
    return result

if __name__ == "_main_":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)