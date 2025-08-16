import requests
from typing import Dict
from config.settings import AUTH_API
from utils.logger import log_metadata


def fetch_user_data(user_id: str) -> Dict[str, any]:
    """
    Fetch user data from the Authentication Server.
    
    Args:
        user_id (str): Unique user identifier.
    
    Returns:
        Dict[str, any]: User data (e.g., {"age": 40, "income": 100000, "risk_tolerance": "balanced"}).
    
    Raises:
        Exception: If fetch fails.
    """
    try:
        # Mock data for local development (replace with real API call in production)
        mock_data = {
            "age": 40,
            "income": 100000,
            "risk_tolerance": "balanced",
            "super_balance": 150000
        }
        log_metadata({
            "service": "user_service",
            "user_id": user_id,
            "status": "success (mock)"
        })
        return mock_data

        # Production code (uncomment when Auth Server is available)
        # url = f"{AUTH_API}/user/{user_id}"
        # response = requests.get(url, timeout=5)
        # response.raise_for_status()
        # user_data = response.json()
        # log_metadata({
        #     "service": "user_service",
        #     "user_id": user_id,
        #     "status": "success"
        # })
        # return user_data
    
    except requests.RequestException as re:
        log_metadata({
            "service": "user_service",
            "user_id": user_id,
            "error": str(re),
            "status": "error"
        })
        raise Exception(f"Failed to fetch user data: {str(re)}")
    except Exception as e:
        log_metadata({
            "service": "user_service",
            "user_id": user_id,
            "error": str(e),
            "status": "error"
        })
        raise Exception(f"Unexpected error fetching user data: {str(e)}")