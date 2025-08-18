from typing import Dict, Any
from services.user_data_service import fetch_user_data
from utils.logger import log_metadata


async def get_user_stock_sentiments(user_id: str, scenario: str = "neutral") -> Dict[str, Dict[str, Any]]:
    """
    Fetch user's stock holdings from Firestore and return their sentiments.

    Args:
        user_id (str): Unique user identifier.
        scenario (str): Economic scenario for sentiment analysis (default: "neutral").

    Returns:
        Dict[str, Dict[str, Any]]: Stock sentiments (e.g., {"BHP.AX": {"sentiment": "positive", "confidence": 0.85}}).

    Raises:
        Exception: If fetch or sentiment analysis fails.
    """
    try:
        # Fetch user data
        user_data = fetch_user_data(user_id)
        stock_symbols = [holding['symbol']
                         for holding in user_data['stock_holdings']]
        print(user_data)
        if not stock_symbols:
            log_metadata({
                "service": "stock_sentiment_service",
                "user_id": user_id,
                "status": "success",
                "message": "No stock holdings found"
            })
            return {}

        # Simulate sentiment analysis (replace with actual /nlp/direct-stock-sentiments logic)
        sentiments = {
            stock: {"sentiment": "positive", "confidence": 0.85}
            for stock in stock_symbols
        }

        log_metadata({
            "service": "stock_sentiment_service",
            "user_id": user_id,
            "status": "success",
            "stocks": stock_symbols,
            "scenario": scenario
        })
        return sentiments

    except Exception as e:
        log_metadata({
            "service": "stock_sentiment_service",
            "user_id": user_id,
            "error": str(e),
            "status": "error"
        })
        raise Exception(f"Failed to fetch stock sentiments: {str(e)}")
