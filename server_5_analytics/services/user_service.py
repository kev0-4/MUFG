from typing import Dict, Any
from datetime import datetime, timedelta
import pandas as pd

def fetch_user_data(user_id: str) -> Dict[str, Any]:
    """
    Mock user data fetch including stock holdings (replacing Firebase).
    
    Args:
        user_id (str): Unique user identifier.
    
    Returns:
        Dict[str, Any]: User data with stock holdings and historical returns.
    """
    # Mock stock price history (daily prices for 1 year)
    dates = [datetime(2024, 8, 17) + timedelta(days=i) for i in range(365)]
    mock_stock_history = {
        "BHP.AX": pd.DataFrame({
            "ds": dates,
            "y": [50.0 + i*0.05 + (i%30)*0.2 for i in range(365)]  # Mock prices
        }),
        "CBA.AX": pd.DataFrame({
            "ds": dates,
            "y": [100.0 + i*0.07 - (i%20)*0.3 for i in range(365)]
        }),
        "WES.AX": pd.DataFrame({
            "ds": dates,
            "y": [60.0 + i*0.04 + (i%25)*0.15 for i in range(365)]
        })
    }

    # Mock user data with stock holdings
    mock_users = {
        "user_123": {
            "user_id": "user_123",
            "age": 40,
            "risk_tolerance": "balanced",
            "super_balance": 100000,
            "historical_return": 0.055,
            "stock_holdings": [
                {"stock": "BHP.AX", "quantity": 100, "historical_data": mock_stock_history["BHP.AX"]},
                {"stock": "CBA.AX", "quantity": 50, "historical_data": mock_stock_history["CBA.AX"]}
            ]
        },
        "user_456": {
            "user_id": "user_456",
            "age": 35,
            "risk_tolerance": "aggressive",
            "super_balance": 80000,
            "historical_return": 0.07,
            "stock_holdings": [
                {"stock": "WES.AX", "quantity": 80, "historical_data": mock_stock_history["WES.AX"]}
            ]
        }
    }
    return mock_users.get(user_id, {
        "user_id": user_id,
        "age": 40,
        "risk_tolerance": "balanced",
        "super_balance": 100000,
        "historical_return": 0.05,
        "stock_holdings": [
            {"stock": "BHP.AX", "quantity": 50, "historical_data": mock_stock_history["BHP.AX"]}
        ]
    })