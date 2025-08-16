# Project: FinGuard Financial and NLP Integration

This repository contains two standalone FastAPI servers:

1. **Financial Server** (port 8001) - Provides stock data APIs.
2. **NLP Server** (port 8000) - Provides NLP services for analyzing financial queries.

---

## Running the Servers
1. **Set Up NLP Server**:
- Navigate: `cd server_4_nlp/`
- Create venv: `python3.11 -m venv nlp_venv`
- Activate: `source nlp_venv/bin/activate`
- Install deps: `pip install -r requirements/dev.txt` (adjust path if needed).

2. **Set Up Financial Server**:
- Navigate: `cd ../finguard-financial-server/` (sibling folder).
- Create venv: `python3 -m venv finance_venv`
- Activate: `source finance_venv/bin/activate`
- Install deps: `pip install -r requirements.txt`.

3. **Configure .env Files** (in each server's folder):
- Financial .env example:
  ```
    # Server Configuration
    HOST=0.0.0.0
    PORT=8001
    DEBUG=true
    LOG_LEVEL=INFO

    # Yahoo Finance Configuration
    YAHOO_FINANCE_ENABLED=true
    YAHOO_FINANCE_RATE_LIMIT=2000

    # Development Settings
    MOCK_DATA_ENABLED=false

    NLP_SERVICE_URL=http://localhost:8000 
  ```
- Restart servers after changes.

## Running the Servers
Use separate terminal windows. Activate venvs in each.
After both servers run:

**Finance Server**
- Use the interactive Swagger UI at [http://localhost:8001/docs](http://localhost:8001/docs) to send requests and view responses.

### 1. Health Check

- **Endpoint:** `GET /api/health`  
- **Purpose:** Check if the server is healthy and running.  
- **How to Test:**  
- Click on `/api/health` in the docs.  
- Click "Try it out" then "Execute".  
- You should receive a response with status "healthy" and current timestamp.

### 2. Get Historical Stock Data

- **Endpoint:** `POST /api/stock/data`  
- **Purpose:** Retrieve historical stock prices for a given ticker and date range.  
- **Request Example:**
```
    {
        “ticker”: “AAPL”,
        “start_date”: “2025-08-14”,
        “end_date”: “2025-08-15”
    }
```
### 3. NLP /nlp/query:
```
curl -X POST "http://localhost:8000/nlp/query" -H "Content-Type: application/json" -d '{"query": "How will a recession affect my super in 20 years?", "user_id": "user_123"}'
```


  
