import torch
import numpy as np
import pandas as pd
import time

def scenario_simulation():
    # 🔹 Hardcoded inputs
    user_id = "user123"
    scenario = "recession"
    monte_carlo_params = {"iterations": 5000, "timeframe": 20, "volatility": 0.15}
    economic_conditions = {"inflation": 0.03}

    # 🔹 Fake user data with two stock holdings
    user_data = {
        "super_balance": 100000,
        "stock_holdings": [
            {
                "stock": "AAPL",
                "quantity": 10,
                "historical_data": pd.DataFrame({"y": np.linspace(100, 200, 100)})
            },
            {
                "stock": "MSFT",
                "quantity": 5,
                "historical_data": pd.DataFrame({"y": np.linspace(50, 120, 100)})
            }
        ]
    }

    initial_balance = user_data.get("super_balance", 100000)
    stock_holdings = user_data.get("stock_holdings", [])
    iterations = monte_carlo_params.get("iterations", 1000)
    timeframe = monte_carlo_params.get("timeframe", 10)
    inflation = economic_conditions.get("inflation", 0.03)

    simulated_balances = []
    for holding in stock_holdings:
        stock = holding["stock"]
        quantity = holding["quantity"]
        historical_data = holding["historical_data"]["y"]

        stock_return = historical_data.pct_change().mean() if len(historical_data) > 1 else 0.05
        stock_volatility = monte_carlo_params.get("volatility", np.std(historical_data) if len(historical_data) > 1 else 0.1)

        returns = torch.normal(mean=stock_return, std=stock_volatility, size=(iterations, timeframe))
        adjusted_returns = returns * (1 - inflation)
        stock_balances = historical_data.iloc[-1] * quantity * torch.cumprod(1 + adjusted_returns, dim=1)
        simulated_balances.append(stock_balances)

    # 🔹 Aggregate portfolio
    total_balances = torch.sum(torch.stack(simulated_balances, dim=0), dim=0) if simulated_balances else torch.ones((iterations, timeframe)) * initial_balance
    simulated_balance = total_balances[:, -1].mean().item()
    confidence_interval = [
        float(torch.quantile(total_balances[:, -1], 0.05).item()),
        float(torch.quantile(total_balances[:, -1], 0.95).item())
    ]

    result = {
        "simulated_balance": round(simulated_balance, 2),
        "confidence_interval": [round(ci, 2) for ci in confidence_interval],
    }

    return result


if __name__ == "__main__":
    start = time.time()
    result = scenario_simulation()
    end = time.time()
    print("Result:", result)
    print(f"⏱ Runtime: {end - start:.4f} seconds")
