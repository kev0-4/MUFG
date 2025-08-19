FinGuard – Financial & NLP Integration
This repository provides two standalone FastAPI servers that together power financial analytics and NLP services for superannuation planning, developed for the MUFG Gen AI Hack ‘25.

🚀 Setup Instructions
1. NLP Server (port 8000)
cd server_4_nlp/
python3.11 -m venv nlp_venv
source nlp_venv/bin/activate   # On Windows: nlp_venv\Scripts\activate
pip install -r requirements/dev.txt
uvicorn main:app --host 0.0.0.0 --port 8000

2. AI Analytics Server (port 8002)
cd ai_analytics_server/
python3.11 -m venv analytics_venv
source analytics_venv/bin/activate   # On Windows: analytics_venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8002

3. Environment Variables
Each server requires its own .env file in the respective directory.
Example for AI Analytics Server (ai_analytics_server/.env):
HOST=0.0.0.0
PORT=8002
DEBUG=true
LOG_LEVEL=INFO
FINANCIAL_SERVER_URL=http://financial-server:8080
REDIS_PASSWORD=your_redis_password
NLP_SERVER_URL=http://nlp-server:8000

Example for NLP Server (server_4_nlp/.env):
HOST=0.0.0.0
PORT=8000
DEBUG=true
LOG_LEVEL=INFO


📡 API Routes
AI Analytics Server (port 8002)
The AI Analytics Server integrates with the Financial Server (http://financial-server:8080) to fetch user portfolio data and the NLP Server (http://nlp-server:8000) for sentiment analysis.
Health Check
GET /api/health – Verify server status.
Request:
curl -X GET "http://localhost:8002/api/health"

Response:
{"status": "healthy"}

Get User Data
POST /analytics/user-data – Fetches user portfolio data, including super_balance and stock_holdings with historical data, from the Financial Server.
Request:
{
  "user_id": "uid1"
}

Response:
{
  "user_id": "uid1",
  "super_balance": 11100.0,
  "stock_holdings": [
    {
      "stock": "BHP.AX",
      "quantity": 100,
      "currentPrice": 27.5,
      "historical_data": [
        {"ds": "2025-08-19T00:00:00.000Z", "y": 27.5}
      ]
    }
  ]
}

Simulate Superannuation
POST /analytics/simulate – Simulates superannuation projections using Prophet forecasting based on user portfolio data.
Request:
{
  "user_id": "uid1",
  "simulation_data": {
    "contribution": 20000,
    "frequency": "quarterly",
    "timeframe": 10,
    "economic_conditions": {"inflation": 0.03}
  }
}

Response:
{
  "projected_balance": 150000.00,
  "forecast": {
    "dates": ["2025-08-19"],
    "values": [11100.00]
  },
  "eli5_response": "Your savings will grow like a steady savings account."
}

Recommend Strategy
POST /analytics/recommend – Generates personalized investment strategy recommendations based on user portfolio and scenario.
Request:
{
  "user_id": "uid1",
  "scenario": "recession"
}

Response:
{
  "user_id": "uid1",
  "recommended_strategy": "Conservative",
  "portfolio_return": 0.05,
  "stocks": ["BHP.AX"]
}

Calibrate Risk
POST /analytics/risk – Calibrates portfolio risk and return based on scenario and economic conditions.
Request:
{
  "user_id": "uid1",
  "scenario": "recession",
  "economic_conditions": {"inflation": 0.03}
}

Response:
{
  "user_id": "uid1",
  "risk_level": "conservative",
  "adjusted_return": 0.033,
  "portfolio_volatility": 0.1
}

Scenario Analysis (Monte Carlo)
POST /analytics/scenario – Runs Monte Carlo simulations with NLP-driven stock sentiments for scenario projections.
Request:
{
  "user_id": "uid1",
  "scenario": "recession",
  "monte_carlo_params": {
    "iterations": 1000,
    "timeframe": 10,
    "volatility": 0.1
  },
  "economic_conditions": {"inflation": 0.03}
}

Response:
{
  "simulated_balance": 120000.00,
  "confidence_interval": [100000.00, 140000.00],
  "stock_sentiments": {
    "BHP.AX": {"sentiment": "positive", "confidence": 0.85}
  },
  "eli5_response": "Your portfolio will grow like a tree in fertile soil."
}

NLP Server (port 8000)
Query Sentiment
POST /nlp/query – Analyzes sentiment for a specific query (e.g., stock in a scenario).
Request:
{
  "query": "BHP.AX recession",
  "user_id": "user_123"
}

Response:
{
  "news_sentiment": {"sentiment": "positive", "confidence": 0.85}
}

Enhance Explanation
POST /nlp/enhance – Converts simulation results into an ELI5 (Explain Like I’m Five) explanation.
Request:
{
  "simulation_data": {"projected_balance": 150000.00, "timeframe": 10},
  "user_id": "user_123",
  "ai_prompt": "Use a savings analogy."
}

Response:
{
  "eli5_response": "Your savings will grow like a steady savings account."
}

Stock Sentiments
POST /nlp/stock-sentiments – Retrieves sentiment for multiple stocks in a scenario.
Request:
{
  "stocks": ["BHP.AX", "AAPL"],
  "scenario": "recession"
}

Response:
{
  "BHP.AX": {"sentiment": "positive", "confidence": 0.85},
  "AAPL": {"sentiment": "neutral", "confidence": 0.70}
}

User Stock Sentiments
POST /nlp/user-stock-sentiments – Retrieves sentiments for a user’s portfolio stocks.
Request:
{
  "userId": "user_123"
}

Response:
{
  "BHP.AX": {"sentiment": "positive", "confidence": 0.85}
}


🖥️ Testing
Swagger UIs

AI Analytics Server: http://localhost:8002/docs
NLP Server: http://localhost:8000/docs

Postman Collection
A Postman collection (FinGuard_Analytics_Server_Updated.postman_collection.json) is provided in the ai_analytics_server/ directory for testing all AI Analytics Server endpoints. Import it into Postman and set the following environment variables:

ANALYTICS_SERVER_URL: http://localhost:8002
FINANCIAL_SERVER_URL: http://financial-server:8080
NLP_SERVER_URL: http://nlp-server:8000

Requirements
Install dependencies for AI Analytics Server:
cd ai_analytics_server/
pip install fastapi uvicorn requests pandas python-dotenv prophet torch redis


📝 Notes

Port Update: The AI Analytics Server runs on port 8002 .
Financial Server Integration: The /analytics/user-data endpoint fetches data from http://financial-server:8001/api/portfolio/{userId} and http://financial-server:8001/api/stock/data.
NLP Integration: The /analytics/scenario endpoint uses http://nlp-server:8001/nlp/user-stock-sentiments for stock sentiments.
Authentication: No headers are required unless specified. Add Authorization headers if needed (e.g., Bearer your_token).
Mocking: Use mock servers for Financial Server (port 8080) and NLP Server (port 8000) if not live (see previous responses for mock code).


------------------------------------------UPDATED TILL UP HERE -----------------------------------------------------------


### 2. Financial Server (port 8001)

```bash
cd ../finguard-financial-server/
python3 -m venv finance_venv
source finance_venv/bin/activate   # On Windows: finance_venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Variables

Each server requires its own `.env`.
Example for **Financial Server**:

```env
HOST=0.0.0.0
PORT=8001
DEBUG=true
LOG_LEVEL=INFO

# Yahoo Finance Config
YAHOO_FINANCE_ENABLED=true
YAHOO_FINANCE_RATE_LIMIT=2000

# Dev settings
MOCK_DATA_ENABLED=false

# Link to NLP Server
NLP_SERVICE_URL=http://localhost:8000
```

---

## 📡 API Routes

### Financial Server (port 8001)

#### Health Check

`GET /api/health` – verify server status.

#### Historical Stock Data

`POST /api/stock/data`
Request:

```json
{
  "ticker": "AAPL",
  "start_date": "2025-08-14",
  "end_date": "2025-08-15"
}
```

#### Simulation

`POST /analytics/simulate`

- Simulates balance projection.

#### Recommendations

`POST /analytics/recommend`

- Suggests strategy and portfolio allocation.

#### Risk Calibration

`POST /analytics/risk`

- Adjusts portfolio risk/return based on scenario.

#### Scenario Analysis (Monte Carlo)

`POST /analytics/scenario`

- Simulates scenarios like recession with confidence intervals.

---

### NLP Server (port 8000)

#### Query Sentiment

`POST /nlp/query`
Request:

```json
{ "query": "BHP.AX recession", "user_id": "user_123" }
```

#### Enhance Explanation

`POST /nlp/enhance`

- Converts simulation results into ELI5 explanation.

#### Stock Sentiments

`POST /nlp/stock-sentiments`

- Retrieves sentiment per stock in a scenario.

#### User Stock Sentiments

`POST /nlp/user-stock-sentiments`
Request:

```json
{ "userId": "user_123" }
```

---

## 🖥️ Testing

Swagger UIs:

- Financial: [http://localhost:8001/docs](http://localhost:8001/docs)
- NLP: [http://localhost:8000/docs](http://localhost:8000/docs)

Postman collection is provided in this repo (`FinGuard AI Analytics & NLP Server.postman_collection.json`) for testing.
