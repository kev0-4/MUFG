---
# FinGuard – Financial & NLP Integration

This repository provides **two standalone FastAPI servers** that together power financial analytics and NLP services.
---

## 🚀 Setup Instructions

### 1. NLP Server (port 8000)

```bash
cd server_4_nlp/
python3.11 -m venv nlp_venv
source nlp_venv/bin/activate   # On Windows: nlp_venv\Scripts\activate
pip install -r requirements/dev.txt
```

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
