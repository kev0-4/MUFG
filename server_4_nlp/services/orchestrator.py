import json
from typing import Dict, Optional, Any
import redis
from services.gemini_service import process_query_with_gemini
from services.nlp_service import analyze_sentiment, fetch_news_sentiment
from services.eli5_service import generate_eli5_response
from utils.logger import log_metadata
from config.settings import REDIS_PASSWORD

# Initialize Redis client (hosted Redis Cloud)
redis_client = redis.Redis(
    host='redis-18927.c212.ap-south-1-1.ec2.redns.redis-cloud.com',
    port=18927,
    username="default",
    password=REDIS_PASSWORD,
    decode_responses=True
)

def orchestrate_query(query: str, user_id: str) -> Dict[str, Any]:
    """
    Orchestrate calls to gemini_service and nlp_service for /nlp/query endpoint.
    
    Args:
        query (str): User query (e.g., "How will a recession affect my super in 20 years?").
        user_id (str): Unique user identifier.
    
    Returns:
        Dict[str, Any]: Combined response with intent, entities, sentiment, and news sentiment.
    
    Raises:
        ValueError: If query is invalid.
        Exception: If service calls fail.
    """
    try:
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")

        # Cache key for query
        cache_key = f"query:{user_id}:{query}"
        cached = redis_client.get(cache_key)
        if cached:
            log_metadata({
                "service": "orchestrator",
                "function": "orchestrate_query",
                "user_id": user_id,
                "query": query[:50],
                "status": "cache_hit"
            })
            return json.loads(cached)

        # Call gemini_service for intent and entities
        gemini_result = process_query_with_gemini(query, user_id)
        intent = gemini_result["intent"]
        entities = gemini_result["entities"]

        # Call nlp_service for query sentiment
        query_sentiment = analyze_sentiment(query, user_id)

        # Call nlp_service for news sentiment if scenario-based
        news_sentiment = None
        if intent == "scenario_simulation" and entities.get("scenario"):
            news_sentiment = fetch_news_sentiment(query, user_id, intent, entities)

        # Combine results
        result = {
            "intent": intent,
            "entities": entities,
            "query_sentiment": query_sentiment,
            "news_sentiment": news_sentiment
        }

        # Cache result (expire in 1 hour)
        redis_client.setex(cache_key, 3600, json.dumps(result))

        log_metadata({
            "service": "orchestrator",
            "function": "orchestrate_query",
            "user_id": user_id,
            "query": query[:50],
            "result": result,
            "status": "success"
        })

        return result

    except ValueError as ve:
        log_metadata({
            "service": "orchestrator",
            "function": "orchestrate_query",
            "user_id": user_id,
            "query": query[:50] if query else "",
            "error": str(ve),
            "status": "error"
        })
        raise
    except redis.RedisError as re:
        log_metadata({
            "service": "orchestrator",
            "function": "orchestrate_query",
            "user_id": user_id,
            "query": query[:50] if query else "",
            "error": str(re),
            "status": "error"
        })
        raise Exception(f"Redis error: {str(re)}")
    except Exception as e:
        log_metadata({
            "service": "orchestrator",
            "function": "orchestrate_query",
            "user_id": user_id,
            "query": query[:50] if query else "",
            "error": str(e),
            "status": "error"
        })
        raise Exception(f"Unexpected error in orchestration: {str(e)}")

def orchestrate_enhance(simulation_data: Dict[str, Any], user_id: str, ai_prompt: Optional[str] = None) -> Dict[str, Any]:
    """
    Orchestrate calls to nlp_service and eli5_service for /nlp/enhance endpoint.
    
    Args:
        simulation_data (Dict[str, Any]): Simulation results (e.g., {"projected_balance": 500000}).
        user_id (str): Unique user identifier.
        ai_prompt (Optional[str]): Optional AI prompt for ELI5 customization.
    
    Returns:
        Dict[str, Any]: Combined response with simulation_data, news_sentiment, and eli5_response.
    
    Raises:
        ValueError: If simulation_data is invalid.
        Exception: If service calls fail.
    """
    try:
        if not simulation_data or not isinstance(simulation_data, dict):
            raise ValueError("Simulation data must be a non-empty dictionary")

        # Cache key for enhance
        cache_key = f"enhance:{user_id}:{json.dumps(simulation_data)}:{ai_prompt or ''}"
        cached = redis_client.get(cache_key)
        if cached:
            log_metadata({
                "service": "orchestrator",
                "function": "orchestrate_enhance",
                "user_id": user_id,
                "simulation_data": simulation_data,
                "status": "cache_hit"
            })
            return json.loads(cached)

        # Call nlp_service for news sentiment if scenario present
        news_sentiment = None
        if simulation_data.get("scenario"):
            # Use scenario as query for news sentiment
            query = f"{simulation_data['scenario']} superannuation"
            news_sentiment = fetch_news_sentiment(query, user_id, "scenario_simulation", {"scenario": simulation_data["scenario"]})

        # Call eli5_service for explanation
        eli5_result = generate_eli5_response(simulation_data, user_id, news_sentiment, ai_prompt)

        # Combine results
        result = {
            "simulation_data": simulation_data,
            "news_sentiment": news_sentiment,
            "eli5_response": eli5_result["eli5_response"]
        }

        # Cache result (expire in 1 hour)
        redis_client.setex(cache_key, 3600, json.dumps(result))

        log_metadata({
            "service": "orchestrator",
            "function": "orchestrate_enhance",
            "user_id": user_id,
            "simulation_data": simulation_data,
            "ai_prompt": ai_prompt,
            "result": result,
            "status": "success"
        })

        return result

    except ValueError as ve:
        log_metadata({
            "service": "orchestrator",
            "function": "orchestrate_enhance",
            "user_id": user_id,
            "simulation_data": simulation_data,
            "error": str(ve),
            "status": "error"
        })
        raise
    except redis.RedisError as re:
        log_metadata({
            "service": "orchestrator",
            "function": "orchestrate_enhance",
            "user_id": user_id,
            "simulation_data": simulation_data,
            "error": str(re),
            "status": "error"
        })
        raise Exception(f"Redis error: {str(re)}")
    except Exception as e:
        log_metadata({
            "service": "orchestrator",
            "function": "orchestrate_enhance",
            "user_id": user_id,
            "simulation_data": simulation_data,
            "error": str(e),
            "status": "error"
        })
        raise Exception(f"Unexpected error in orchestration: {str(e)}")