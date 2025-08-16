from typing import Dict, Optional
from services.user_service import fetch_user_data
from utils.logger import log_metadata

def generate_eli5_response(simulation_data: Dict[str, any], user_id: str, news_context: Optional[Dict[str, any]] = None) -> str:
    """
    Generate a simplified ELI5 explanation for financial simulation data.
    
    Args:
        simulation_data (Dict[str, any]): Simulation results (e.g., {"projected_balance": 500000, "scenario": "recession", "timeframe": 20, "risk_level": "balanced"}).
        user_id (str): Unique user identifier for logging and context.
        news_context (Optional[Dict[str, any]]): News sentiment and summary (e.g., {"sentiment": -0.5, "summary": "Economic downturn predicted"}).
    
    Returns:
        str: ELI5 explanation (e.g., "Your super is like a savings jar...").
    
    Raises:
        ValueError: If simulation_data is empty or invalid.
        Exception: If response generation fails.
    """
    try:
        if not simulation_data or not isinstance(simulation_data, dict):
            raise ValueError("Simulation data must be a non-empty dictionary")

        # Fetch user data for personalization
        user_data = fetch_user_data(user_id)
        age = user_data.get("age", "unknown")
        risk_tolerance = user_data.get("risk_tolerance", "unknown")

        # Extract simulation data
        projected_balance = simulation_data.get("projected_balance", 0)
        scenario = simulation_data.get("scenario", None)
        timeframe = simulation_data.get("timeframe", 0)
        risk_level = simulation_data.get("risk_level", "unknown")
        contribution = simulation_data.get("contribution", None)
        frequency = simulation_data.get("frequency", None)

        # Base ELI5 response
        response = f"Your super is like a savings jar that grows over time. "
        
        # Personalize based on user data
        if age != "unknown" and isinstance(age, int):
            response += f"Since you’re {age}, it’s like saving for a big trip when you’re older. "
        else:
            response += "It’s like saving for something cool in the future. "

        # Add contribution details if available
        if contribution and frequency:
            response += f"By adding ${contribution:,} {frequency}, "
        elif contribution:
            response += f"By adding ${contribution:,}, "

        # Add projection and timeframe
        response += f"your jar could have ${projected_balance:,} in {timeframe} years"

        # Add scenario context if present
        if scenario:
            response += f", but a {scenario} might make it grow slower, like when it’s harder to save during a rainy day. "
            if news_context and news_context.get("sentiment", 0) < 0:
                response += f"News says things might be tough ({news_context['summary']}), so your jar might need extra care. "
            elif news_context:
                response += f"News says things are okay ({news_context['summary']}), so your jar should keep growing. "
        else:
            response += f". "

        # Add risk level or tolerance
        if risk_level != "unknown":
            response += f"You’re in a {risk_level}-risk fund, which is like choosing a {risk_level} path—safer or riskier—for your savings. "
        elif risk_tolerance != "unknown":
            response += f"Your {risk_tolerance} risk style means you’re choosing a {risk_tolerance} path for your savings. "

        # Final touch
        response += "Keep adding to your jar, and it’ll grow nicely for your future!"

        log_metadata({
            "service": "eli5_service",
            "function": "generate_eli5_response",
            "user_id": user_id,
            "simulation_data": simulation_data,
            "news_context": news_context,
            "response": response[:50],  # Truncate for logging
            "status": "success"
        })

        return response

    except ValueError as ve:
        log_metadata({
            "service": "eli5_service",
            "function": "generate_eli5_response",
            "user_id": user_id,
            "simulation_data": simulation_data,
            "error": str(ve),
            "status": "error"
        })
        raise
    except Exception as e:
        log_metadata({
            "service": "eli5_service",
            "function": "generate_eli5_response",
            "user_id": user_id,
            "simulation_data": simulation_data,
            "error": str(e),
            "status": "error"
        })
        raise Exception(f"Unexpected error in ELI5 response generation: {str(e)}")

if __name__ == "__main__":
    user_id = "user_123"
    test_cases = [
        {
            "simulation_data": {
                "projected_balance": 500000,
                "scenario": "recession",
                "timeframe": 20,
                "risk_level": "balanced"
            },
            "news_context": {
                "sentiment": -0.5,
                "summary": "Mock: 2% Economic Downturn Predicted for Australia in 2025"
            }
        },
        {
            "simulation_data": {
                "projected_balance": 750000,
                "timeframe": 10,
                "contribution": 20000,
                "frequency": "quarterly"
            },
            "news_context": None
        },
        {
            "simulation_data": {
                "projected_balance": 300000,
                "risk_level": "low",
                "scenario": None
            },
            "news_context": {
                "sentiment": 0.7,
                "summary": "Mock: Superannuation Market Stable in 2025"
            }
        }
    ]

    for case in test_cases:
        print("\nSimulation Data:", case["simulation_data"])
        print("News Context:", case["news_context"])
        response = generate_eli5_response(case["simulation_data"], user_id, case["news_context"])
        print("ELI5 Response:", response)