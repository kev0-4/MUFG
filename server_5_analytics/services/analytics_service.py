import pandas as pd
import redis
import requests
import torch
from typing import Dict, Optional, Any
from prophet import Prophet
from config.settings import REDIS_PASSWORD, NLP_SERVER_URL
from utils.logger import log_metadata
from services.user_service import fetch_user_data
import json
import numpy as np
from datetime import datetime, timedelta

# Initialize Redis client
redis_client = redis.Redis(
    host='redis-18927.c212.ap-south-1-1.ec2.redns.redis-cloud.com',
    port=18927,
    username="default",
    password=REDIS_PASSWORD,
    decode_responses=True
)


def simulate_superannuation(simulation_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """
    Simulate superannuation projections using Prophet with stock holdings.

    Args:
        simulation_data (Dict[str, Any]): Input data (e.g., {"contribution": 20000, "frequency": "quarterly", "timeframe": 10, "economic_conditions": {"inflation": 0.03}}).
        user_id (str): Unique user identifier.

    Returns:
        Dict[str, Any]: Forecasted balance and ELI5 explanation.
    """
    try:
        if not simulation_data or not isinstance(simulation_data, dict):
            raise ValueError("Simulation data must be a non-empty dictionary")

        # Cache key
        cache_key = f"simulate:{user_id}:{json.dumps(simulation_data)}"
        cached = redis_client.get(cache_key)
        if cached:
            log_metadata({
                "service": "analytics_service",
                "function": "simulate_superannuation"
            })
            return json.loads(cached)

        # Fetch user data
        user_data = fetch_user_data(user_id)
        initial_balance = user_data.get("super_balance", 100000)
        contribution = simulation_data.get("contribution", 0)
        timeframe = simulation_data.get("timeframe", 10)
        frequency = simulation_data.get("frequency", "yearly")
        economic_conditions = simulation_data.get(
            "economic_conditions", {"inflation": 0.03})
        stock_holdings = user_data.get("stock_holdings", [])

        # Map frequency to Prophet-compatible aliases
        frequency_map = {
            "yearly": "Y",
            "quarterly": "Q",
            "monthly": "M"
        }
        prophet_freq = frequency_map.get(frequency, "Y")
        periods_per_year = {"yearly": 1, "quarterly": 4,
                            "monthly": 12}.get(frequency, 1)

        # Aggregate stock portfolio value
        portfolio_values = []
        for holding in stock_holdings:
            df = holding["historical_data"].copy()
            df["y"] = df["y"] * holding["quantity"]  # Scale by quantity
            portfolio_values.append(df)

        if portfolio_values:
            portfolio_df = pd.concat(
                [df.set_index("ds") for df in portfolio_values], axis=1).sum(axis=1).reset_index()
            portfolio_df.columns = ["ds", "y"]
        else:
            # Fallback to initial balance
            dates = [datetime(2025, 1, 1) + timedelta(days=i*365)
                     for i in range(2)]
            portfolio_df = pd.DataFrame(
                {"ds": dates, "y": [initial_balance]*2})

        # Prophet forecasting
        model = Prophet(yearly_seasonality=True,
                        weekly_seasonality=False, daily_seasonality=False)
        model.fit(portfolio_df)
        future = model.make_future_dataframe(
            periods=timeframe*periods_per_year, freq=prophet_freq)
        forecast = model.predict(future)

        projected_balance = forecast["yhat"].iloc[-1] + contribution * \
            timeframe * (1 - economic_conditions["inflation"])

        # Convert Timestamps to strings
        forecast_dates = [ts.strftime("%Y-%m-%d")
                          for ts in forecast["ds"].iloc[-10:]]

        # Call NLP Server for ELI5
        nlp_response = requests.post(
            f"{NLP_SERVER_URL}/nlp/enhance",
            json={"simulation_data": {"projected_balance": projected_balance,
                                      "timeframe": timeframe}, "user_id": user_id, "ai_prompt": "Use a savings analogy."},
            timeout=1000
        )
        nlp_response.raise_for_status()
        eli5_response = nlp_response.json().get(
            "eli5_response", "Your savings will grow like a steady savings account.")

        result = {
            "projected_balance": round(projected_balance, 2),
            "forecast": {"dates": forecast_dates, "values": [round(v, 2) for v in forecast["yhat"].tolist()[-10:]]},
            "eli5_response": eli5_response
        }

        # Cache result
        try:
            redis_client.setex(cache_key, 3600, json.dumps(result))
        except TypeError as te:
            log_metadata({
                "service": "analytics_service",
                "function": "simulate_superannuation",
            })
            raise Exception(f"Failed to cache result: {str(te)}")

        log_metadata({
            "service": "analytics_service",
            "function": "simulate_superannuation"
        })
        return result

    except ValueError as ve:
        log_metadata({
            "service": "analytics_service",
            "function": "simulate_superannuation"
        })
        raise
    except requests.RequestException as re:
        log_metadata({
            "service": "analytics_service",
            "function": "simulate_superannuation",
            "status": "error"
        })
        raise Exception(f"NLP Server error: {str(re)}")
    except Exception as e:
        log_metadata({
            "service": "analytics_service",
            "function": "simulate_superannuation"
        })
        raise Exception(f"Unexpected error in simulation: {str(e)}")


def recommend_strategy(user_id: str, scenario: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate personalized recommendations based on user data and stock holdings.

    Args:
        user_id (str): Unique user identifier.
        scenario (Optional[str]): Scenario (e.g., "recession").

    Returns:
        Dict[str, Any]: Recommended strategy and metrics.
    """
    try:
        if not user_id or not isinstance(user_id, str):
            raise ValueError("User ID must be a non-empty string")

        # Cache key
        cache_key = f"recommend:{user_id}:{scenario or ''}"
        cached = redis_client.get(cache_key)
        if cached:
            log_metadata({
                "service": "analytics_service",
                "function": "recommend_strategy"
            })
            return json.loads(cached)

        # Fetch user data
        user_data = fetch_user_data(user_id)
        stock_holdings = user_data.get("stock_holdings", [])
        risk_tolerance = "balanced"  # Mocked, as not in Financial Server
        historical_return = 0.05  # Mocked, as not in Financial Server

        # Calculate portfolio return
        portfolio_return = sum(holding["historical_data"]["y"].mean() * holding["quantity"] for holding in stock_holdings) / sum(
            holding["quantity"] for holding in stock_holdings) if stock_holdings else historical_return

        # Adjust recommendation
        strategy = risk_tolerance.capitalize()
        if scenario == "recession":
            strategy = "Conservative" if risk_tolerance != "aggressive" else "Balanced"
        elif scenario == "growth":
            strategy = "Aggressive" if risk_tolerance != "conservative" else "Balanced"

        result = {
            "user_id": user_id,
            "recommended_strategy": strategy,
            "portfolio_return": round(portfolio_return, 4),
            "stocks": [holding["stock"] for holding in stock_holdings]
        }

        # Cache result
        redis_client.setex(cache_key, 3600, json.dumps(result))

        log_metadata({
            "service": "analytics_service",
            "function": "recommend_strategy"
        })
        return result

    except ValueError as ve:
        log_metadata({
            "service": "analytics_service",
        })
        raise
    except Exception as e:
        log_metadata({
            "service": "analytics_service",
            "function": "recommend_strategy"
        })
        raise Exception(f"Unexpected error in recommendation: {str(e)}")


def calibrate_risk(user_id: str, scenario: str, economic_conditions: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calibrate risk based on stock holdings and economic conditions.

    Args:
        user_id (str): Unique user identifier.
        scenario (str): Scenario (e.g., "recession").
        economic_conditions (Dict[str, Any]): Economic factors (e.g., {"inflation": 0.03}).

    Returns:
        Dict[str, Any]: Adjusted risk level and return.
    """
    try:
        if not user_id or not isinstance(user_id, str):
            raise ValueError("User ID must be a non-empty string")
        if not scenario or not isinstance(scenario, str):
            raise ValueError("Scenario must be a non-empty string")

        # Cache key
        cache_key = f"risk:{user_id}:{scenario}:{json.dumps(economic_conditions)}"
        cached = redis_client.get(cache_key)
        if cached:
            log_metadata({
                "service": "analytics_service",
                "function": "calibrate_risk"
            })
            return json.loads(cached)

        # Fetch user data
        user_data = fetch_user_data(user_id)
        stock_holdings = user_data.get("stock_holdings", [])
        risk_tolerance = "balanced"  # Mocked, as not in Financial Server
        inflation = economic_conditions.get("inflation", 0.03)

        # Calculate portfolio volatility
        portfolio_volatility = sum(np.std(holding["historical_data"]["y"]) * holding["quantity"] for holding in stock_holdings) / sum(
            holding["quantity"] for holding in stock_holdings) if stock_holdings else 0.1

        # Adjust return
        risk_multipliers = {"recession": 0.7, "balanced": 1.0, "growth": 1.3}
        adjusted_return = sum(holding["historical_data"]["y"].mean() * holding["quantity"] for holding in stock_holdings) / sum(
            holding["quantity"] for holding in stock_holdings) if stock_holdings else 0.05
        adjusted_return *= risk_multipliers.get(
            scenario, 1.0) * (1 - inflation)
        risk_level = risk_tolerance if scenario != "recession" else "conservative"

        result = {
            "user_id": user_id,
            "risk_level": risk_level,
            "adjusted_return": round(adjusted_return, 4),
            "portfolio_volatility": round(portfolio_volatility, 4)
        }

        # Cache result
        redis_client.setex(cache_key, 3600, json.dumps(result))

        log_metadata({
            "service": "analytics_service",
            "function": "calibrate_risk"
        })
        return result

    except ValueError as ve:
        log_metadata({
            "service": "analytics_service",
            "function": "calibrate_risk"
        })
        raise
    except Exception as e:
        log_metadata({
            "service": "analytics_service",
            "function": "calibrate_risk"
        })
        raise Exception(f"Unexpected error in risk calibration: {str(e)}")


def scenario_simulation(user_id: str, scenario: str, monte_carlo_params: Dict[str, Any], economic_conditions: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run Monte Carlo simulation for scenario projections with stock-specific sentiment.

    Args:
        user_id (str): Unique user identifier.
        scenario (str): Scenario (e.g., "recession").
        monte_carlo_params (Dict[str, Any]): Simulation params (e.g., {"iterations": 1000, "volatility": 0.1}).
        economic_conditions (Dict[str, Any]): Economic factors (e.g., {"inflation": 0.03}).

    Returns:
        Dict[str, Any]: Simulated balance, confidence interval, stock sentiments, and ELI5.
    """
    try:
        if not user_id or not isinstance(user_id, str):
            raise ValueError("User ID must be a non-empty string")
        if not scenario or not isinstance(scenario, str):
            raise ValueError("Scenario must be a non-empty string")

        # Cache key
        cache_key = f"scenario:{user_id}:{scenario}:{json.dumps(monte_carlo_params)}:{json.dumps(economic_conditions)}"
        cached = redis_client.get(cache_key)
        if cached:
            log_metadata({
                "service": "analytics_service",
                "function": "scenario_simulation"
            })
            return json.loads(cached)

        # Fetch user data
        user_data = fetch_user_data(user_id)
        initial_balance = user_data.get("super_balance", 100000)
        stock_holdings = user_data.get("stock_holdings", [])
        iterations = monte_carlo_params.get("iterations", 1000)
        timeframe = monte_carlo_params.get("timeframe", 10)
        inflation = economic_conditions.get("inflation", 0.03)

        # Monte Carlo simulation
        simulated_balances = []
        for holding in stock_holdings:
            stock = holding["stock"]
            quantity = holding["quantity"]
            historical_data = holding["historical_data"]["y"]
            stock_return = historical_data.pct_change(
            ).mean() if len(historical_data) > 1 else 0.05
            stock_volatility = monte_carlo_params.get("volatility", np.std(
                historical_data) if len(historical_data) > 1 else 0.1)

            returns = torch.normal(
                mean=stock_return, std=stock_volatility, size=(iterations, timeframe))
            adjusted_returns = returns * (1 - inflation)
            stock_balances = historical_data.iloc[-1] * \
                quantity * torch.cumprod(1 + adjusted_returns, dim=1)
            simulated_balances.append(stock_balances)

        # Aggregate portfolio
        total_balances = torch.sum(torch.stack(simulated_balances, dim=0), dim=0) if simulated_balances else torch.ones(
            (iterations, timeframe)) * initial_balance
        simulated_balance = total_balances[:, -1].mean().item()
        confidence_interval = [
            float(torch.quantile(total_balances[:, -1], 0.05).item()),
            float(torch.quantile(total_balances[:, -1], 0.95).item())
        ]

        # Fetch stock-specific sentiments from NLP Server
        nlp_response = requests.post(
            f"{NLP_SERVER_URL}/nlp/user-stock-sentiments",
            json={"userId": user_id},
            timeout=1200
        )
        nlp_response.raise_for_status()
        stock_sentiments = nlp_response.json()

        # Call NLP Server for ELI5
        nlp_enhance_response = requests.post(
            f"{NLP_SERVER_URL}/nlp/enhance",
            json={"simulation_data": {"projected_balance": simulated_balance, "scenario": scenario,
                                      "timeframe": timeframe}, "user_id": user_id, "ai_prompt": "Use a growth analogy."},
            timeout=1200
        )
        nlp_enhance_response.raise_for_status()
        eli5_response = nlp_enhance_response.json().get(
            "eli5_response", "Your portfolio will grow like a tree in fertile soil.")

        result = {
            "simulated_balance": round(simulated_balance, 2),
            "confidence_interval": [round(ci, 2) for ci in confidence_interval],
            "stock_sentiments": stock_sentiments,
            "eli5_response": eli5_response
        }

        # Cache result
        redis_client.setex(cache_key, 3600, json.dumps(result))

        log_metadata({
            "service": "analytics_service",
            "function": "scenario_simulation"
        })
        return result

    except ValueError as ve:
        log_metadata({
            "service": "analytics_service",
            "function": "scenario_simulation",
        })
        raise
    except requests.RequestException as re:
        log_metadata({
            "service": "analytics_service",
            "function": "scenario_simulation",
        })
        raise Exception(f"NLP Server error: {str(re)}")
    except Exception as e:
        log_metadata({
            "service": "analytics_service",
            "function": "scenario_simulation",
        })
        raise Exception(f"Unexpected error in scenario simulation: {str(e)}")
