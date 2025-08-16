import pytest
from fastapi.testclient import TestClient
from datetime import date, timedelta

from app.main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_stock_data_endpoint():
    """Test stock data retrieval"""
    payload = {
        "ticker": "AAPL",
        "start_date": str(date.today() - timedelta(days=30)),
        "end_date": str(date.today() - timedelta(days=1))
    }
    
    response = client.post("/api/stock/data", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert len(data["prices"]) > 0
    assert "last_updated" in data

def test_invalid_ticker():
    """Test handling of invalid ticker"""
    payload = {
        "ticker": "INVALID_TICKER_THAT_DOES_NOT_EXIST",
        "start_date": str(date.today() - timedelta(days=30)),
        "end_date": str(date.today() - timedelta(days=1))
    }
    
    response = client.post("/api/stock/data", json=payload)
    # Should handle gracefully, either return empty data or 404
    assert response.status_code in [200, 404]

def test_future_date_validation():
    """Test that future dates are rejected"""
    payload = {
        "ticker": "AAPL",
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=1))
    }
    
    response = client.post("/api/stock/data", json=payload)
    assert response.status_code == 400

def test_news_endpoint():
    """Test news retrieval"""
    payload = {
        "query": "recession",
        "limit": 5
    }
    
    response = client.post("/api/news", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["query"] == "recession"
    assert len(data["articles"]) <= 5

def test_latest_stock_price():
    """Test latest stock price endpoint"""
    response = client.get("/api/stock/latest/AAPL")
    assert response.status_code == 200
    
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert "latest_price" in data
    assert "as_of_date" in data

if __name__ == "__main__":
    pytest.main([__file__])
