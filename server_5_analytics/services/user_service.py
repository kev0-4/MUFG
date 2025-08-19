from typing import Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import requests
from config.settings import FINANCIAL_SERVER_URL
from utils.logger import log_metadata


def fetch_user_data(user_id: str) -> Dict[str, Any]:
    """
    Fetch user data from Financial Server, including stock holdings and historical data.

    Args:
        user_id (str): Unique user identifier.

    Returns:
        Dict[str, Any]: User data with user_id, super_balance, and stock_holdings.

    Raises:
        ValueError: If user_id is invalid or user not found.
        Exception: For other API errors.
    """
    try:
        if not user_id:
            raise ValueError("User ID must be a non-empty string")

        # Fetch portfolio data
        portfolio_url = f"{FINANCIAL_SERVER_URL}/api/portfolio/{user_id}"
        portfolio_response = requests.get(portfolio_url, timeout=5)
        portfolio_response.raise_for_status()
        portfolio_data = portfolio_response.json()
        # print("FINANCIAL_SERVER_URL:", FINANCIAL_SERVER_URL)
        # print("User ID:", user_id)
        # print("Portfolio URL:", portfolio_url)
        # print("Portfolio Response (raw):", portfolio_response.text)
        # print("Portfolio Data (parsed):", portfolio_data)

        # Validate response
        if not portfolio_data.get("user") or not portfolio_data.get("portfolio") or not portfolio_data.get("holdings"):
            raise ValueError(f"Invalid portfolio data for user {user_id}")
        print("---Passed validate response---")
        # Fetch historical data for stocks
        stock_holdings = []
        start_date = (datetime.now() - timedelta(days=365)
                      ).strftime("%Y-%m-%d")  # 1 year ago
        end_date = datetime.now().strftime("%Y-%m-%d")  # Today
        for holding in portfolio_data["holdings"]:
            if holding["assetType"] != "stock":
                continue

            # Fetch historical stock data
            stock_data_url = f"{FINANCIAL_SERVER_URL}/api/stock/data"
            stock_data_payload = {
                "ticker": holding["symbol"],
                "start_date": start_date,
                "end_date": end_date
            }
            stock_data_response = requests.post(
                stock_data_url, json=stock_data_payload, timeout=5)
            stock_data_response.raise_for_status()
            stock_data = stock_data_response.json()

            # Convert prices to DataFrame
            historical_data = pd.DataFrame(stock_data["prices"])
            if not historical_data.empty:
                historical_data["ds"] = pd.to_datetime(historical_data["date"])
                historical_data["y"] = historical_data["close"].astype(float)
                historical_data = historical_data[["ds", "y"]]
            else:
                # Fallback: Use currentPrice for a single data point
                historical_data = pd.DataFrame({
                    "ds": [datetime.now()],
                    "y": [holding["currentPrice"]]
                })

            stock_holdings.append({
                "stock": holding["symbol"],
                "quantity": holding["quantity"],
                "currentPrice": holding["currentPrice"],
                "historical_data": historical_data
            })

        # Construct response
        result = {
            "user_id": user_id,
            "super_balance": portfolio_data["portfolio"]["totalValue"],
            "stock_holdings": stock_holdings
            # Note: age, risk_tolerance, historical_return not available in Financial Server
        }
        # print("----printing results----")
        # print(result)
        print("--got results from user_Service just before returning--")
        # log_metadata({
        #     "service": "user_service",
        #     "function": "fetch_user_data",
        #     "user_id": user_id,
        #     "status": "success",
        #     "result": result
        # })
        return result

    except ValueError as ve:
        log_metadata({
            "service": "user_service",
            "function": "fetch_user_data",
            "user_id": user_id,
            "error": str(ve),
            "status": "error"
        })
        raise ValueError(f"Failed to fetch user data: {str(ve)}")
    except requests.RequestException as re:
        log_metadata({
            "service": "user_service",
            "function": "fetch_user_data",
            "user_id": user_id,
            "error": str(re),
            "status": "error"
        })
        raise Exception(f"Financial Server error: {str(re)}")
    except Exception as e:
        log_metadata({
            "service": "user_service",
            "function": "fetch_user_data",
            "user_id": user_id,
            "error": str(e),
            "status": "error"
        })
        raise Exception(f"Unexpected error fetching user data: {str(e)}")
