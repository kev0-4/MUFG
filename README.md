# FinGuard – Financial & NLP Integration

![FinGuard Banner](https://via.placeholder.com/800x200?text=FinGuard+Financial+Analytics+and+NLP+Services)

A powerful integration of financial analytics and natural language processing services designed for superannuation planning, developed for the MUFG Gen AI Hack ‘25. This system consists of two independent FastAPI servers that work together to provide comprehensive financial insights with explainable AI.

## 🚀 Quick Start

### Prerequisites
- Python 3.11
- pip (Python package manager)
- Redis (for caching, if needed)

### Installation & Setup

#### 1. NLP Server (Port 8000)
```bash
cd server_4_nlp/
python3.11 -m venv nlp_venv
source nlp_venv/bin/activate  # On Windows: nlp_venv\Scripts\activate
pip install -r requirements/dev.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. AI Analytics Server (Port 8002)
```bash
cd ai_analytics_server/
python3.11 -m venv analytics_venv
source analytics_venv/bin/activate  # On Windows: analytics_venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

### Environment Configuration

Each server requires its own `.env` file:

#### AI Analytics Server (ai_analytics_server/.env)
```env
HOST=0.0.0.0
PORT=8002
DEBUG=true
LOG_LEVEL=INFO
FINANCIAL_SERVER_URL=http://financial-server:8080
REDIS_PASSWORD=your_redis_password
NLP_SERVER_URL=http://nlp-server:8000
```

#### NLP Server (server_4_nlp/.env)
```env
HOST=0.0.0.0
PORT=8000
DEBUG=true
LOG_LEVEL=INFO
```

## 📡 API Documentation

### AI Analytics Server (Port 8002)

The AI Analytics Server integrates with external financial services and the NLP server to provide comprehensive financial analytics.

#### Health Check
- **Endpoint**: `GET /api/health`
- **Description**: Verify server status
- **Example**:
  ```bash
  curl -X GET "http://localhost:8002/api/health"
  ```
- **Response**:
  ```json
  {"status": "healthy"}
  ```

#### Get User Data
- **Endpoint**: `POST /analytics/user-data`
- **Description**: Fetches user portfolio data including super balance and stock holdings
- **Request**:
  ```json
  {
    "user_id": "uid1"
  }
  ```
- **Response**:
  ```json
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
  ```

#### Simulate Superannuation
- **Endpoint**: `POST /analytics/simulate`
- **Description**: Projects superannuation growth using Prophet forecasting
- **Request**:
  ```json
  {
    "user_id": "uid1",
    "simulation_data": {
      "contribution": 20000,
      "frequency": "quarterly",
      "timeframe": 10,
      "economic_conditions": {"inflation": 0.03}
    }
  }
  ```
- **Response**:
  ```json
  {
    "projected_balance": 150000.00,
    "forecast": {
      "dates": ["2025-08-19"],
      "values": [11100.00]
    },
    "eli5_response": "Your savings will grow like a steady savings account."
  }
  ```

#### Recommend Strategy
- **Endpoint**: `POST /analytics/recommend`
- **Description**: Generates personalized investment recommendations
- **Request**:
  ```json
  {
    "user_id": "uid1",
    "scenario": "recession"
  }
  ```
- **Response**:
  ```json
  {
    "user_id": "uid1",
    "recommended_strategy": "Conservative",
    "portfolio_return": 0.05,
    "stocks": ["BHP.AX"]
  }
  ```

#### Calibrate Risk
- **Endpoint**: `POST /analytics/risk`
- **Description**: Adjusts portfolio risk based on economic conditions
- **Request**:
  ```json
  {
    "user_id": "uid1",
    "scenario": "recession",
    "economic_conditions": {"inflation": 0.03}
  }
  ```
- **Response**:
  ```json
  {
    "user_id": "uid1",
    "risk_level": "conservative",
    "adjusted_return": 0.033,
    "portfolio_volatility": 0.1
  }
  ```

#### Scenario Analysis (Monte Carlo)
- **Endpoint**: `POST /analytics/scenario`
- **Description**: Runs Monte Carlo simulations with NLP-driven sentiments
- **Request**:
  ```json
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
  ```
- **Response**:
  ```json
  {
    "simulated_balance": 120000.00,
    "confidence_interval": [100000.00, 140000.00],
    "stock_sentiments": {
      "BHP.AX": {"sentiment": "positive", "confidence": 0.85}
    },
    "eli5_response": "Your portfolio will grow like a tree in fertile soil."
  }
  ```

### NLP Server (Port 8000)

#### Query Sentiment
- **Endpoint**: `POST /nlp/query`
- **Description**: Analyzes sentiment for specific queries
- **Request**:
  ```json
  {
    "query": "BHP.AX recession",
    "user_id": "user_123"
  }
  ```
- **Response**:
  ```json
  {
    "news_sentiment": {"sentiment": "positive", "confidence": 0.85}
  }
  ```

#### Enhance Explanation
- **Endpoint**: `POST /nlp/enhance`
- **Description**: Converts technical results into simple explanations
- **Request**:
  ```json
  {
    "simulation_data": {"projected_balance": 150000.00, "timeframe": 10},
    "user_id": "user_123",
    "ai_prompt": "Use a savings analogy."
  }
  ```
- **Response**:
  ```json
  {
    "eli5_response": "Your savings will grow like a steady savings account."
  }
  ```

#### Stock Sentiments
- **Endpoint**: `POST /nlp/stock-sentiments`
- **Description**: Retrieves sentiment for multiple stocks
- **Request**:
  ```json
  {
    "stocks": ["BHP.AX", "AAPL"],
    "scenario": "recession"
  }
  ```
- **Response**:
  ```json
  {
    "BHP.AX": {"sentiment": "positive", "confidence": 0.85},
    "AAPL": {"sentiment": "neutral", "confidence": 0.70}
  }
  ```

#### User Stock Sentiments
- **Endpoint**: `POST /nlp/user-stock-sentiments`
- **Description**: Retrieves sentiments for a user's portfolio
- **Request**:
  ```json
  {
    "userId": "user_123"
  }
  ```
- **Response**:
  ```json
  {
    "BHP.AX": {"sentiment": "positive", "confidence": 0.85}
  }
  ```

## 🖥️ Testing & Development

### Interactive API Documentation
- **AI Analytics Server**: http://localhost:8002/docs
- **NLP Server**: http://localhost:8000/docs

### Postman Collection
A Postman collection (`FinGuard_Analytics_Server_Updated.postman_collection.json`) is provided in the `ai_analytics_server/` directory. Import it into Postman and set these environment variables:

```env
ANALYTICS_SERVER_URL: http://localhost:8002
FINANCIAL_SERVER_URL: http://financial-server:8080
NLP_SERVER_URL: http://nlp-server:8000
```

### Dependencies

#### AI Analytics Server
```bash
cd ai_analytics_server/
pip install fastapi uvicorn requests pandas python-dotenv prophet torch redis
```

#### NLP Server
```bash
cd server_4_nlp/
pip install -r requirements/dev.txt
```


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
