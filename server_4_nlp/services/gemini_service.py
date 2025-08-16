import os
import re
import json
from typing import Dict
import google.generativeai as genai
from google.generativeai import GenerativeModel
from google.api_core.exceptions import GoogleAPIError
from config.settings import GEMINI_API_KEY
from utils.logger import log_metadata
from services.user_data_service import fetch_user_data


def parse_fallback(query: str) -> Dict[str, any]:
    """
    Fallback parser using regex and keyword matching for query parsing.

    Args:
        query (str): User query to parse.

    Returns:
        Dict[str, any]: Parsed intent, entities, and descriptive text.
    """
    query_lower = query.lower()
    entities = {}

    # Intent and scenario
    if "recession" in query_lower:
        intent = "scenario_simulation"
        entities["scenario"] = "recession"
    elif "super" in query_lower and ("how much" in query_lower or "grow" in query_lower):
        intent = "super_projection"
    else:
        intent = "general_query"

    # Timeframe (e.g., "20 years", "10 year")
    match_timeframe = re.search(r"(\d+)\s*year", query_lower)
    if match_timeframe:
        entities["timeframe"] = int(match_timeframe.group(1))

    # Contribution (e.g., "$20k", "20000", "20,000")
    match_contribution = re.search(
        r"\$?\s*(\d{1,3}(?:,\d{3})*|\d+)(k)?", query_lower)
    if match_contribution:
        amount = match_contribution.group(1).replace(",", "")
        amount = int(amount)
        if match_contribution.group(2):  # 'k' present
            amount *= 1000
        entities["contribution"] = amount

    # Frequency mapping
    freq_map = {
        "annually": "annually",
        "yearly": "annually",
        "monthly": "monthly",
        "bi-annual": "bi-annual",
        "biannual": "bi-annual",
        "semi-annual": "bi-annual",
        "quarterly": "quarterly",
        "every 4 months": "every 4 months",
        "4 months": "every 4 months",
        "weekly": "weekly"
    }
    for key, value in freq_map.items():
        if key in query_lower:
            entities["frequency"] = value
            break

    # Additional entities (investment type, risk tolerance)
    if "balanced fund" in query_lower:
        entities["investment_type"] = "balanced_fund"
    elif "fixed income" in query_lower:
        entities["investment_type"] = "fixed_income"
    if "low risk" in query_lower:
        entities["risk_tolerance"] = "low"
    elif "high risk" in query_lower:
        entities["risk_tolerance"] = "high"

    return {
        "intent": intent,
        "entities": entities,
        "descriptive_text": f"Fallback parse: User asked '{query}'"
    }


def process_query_with_gemini(query: str, user_id: str) -> Dict[str, any]:
    try:
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")

        # Fetch user data context
        user_data = fetch_user_data(user_id)
        user_context = (
            f"User context: age {user_data.get('age', 'unknown')}, "
            f"income ${user_data.get('income', 'unknown')}, "
            f"risk tolerance {user_data.get('risk_tolerance', 'unknown')}, "
            f"current super balance ${user_data.get('super_balance', 'unknown')}."
        )

        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")

        # Schema definition with descriptive_text
        schema = {
            "type": "object",
            "properties": {
                "intent": {
                    "type": "string",
                    "enum": ["scenario_simulation", "super_projection", "general_query"]
                },
                "entities": {
                    "type": "object",
                    "properties": {
                        "scenario": {
                            "type": "string",
                            "nullable": True
                        },
                        "timeframe": {
                            "type": "integer",
                            "nullable": True
                        },
                        "contribution": {
                            "type": "integer",
                            "nullable": True
                        },
                        "frequency": {
                            "type": "string",
                            "enum": [
                                "annually",
                                "bi-annual",
                                "quarterly",
                                "monthly",
                                "weekly",
                                "every 4 months",
                                "custom"
                            ],
                            "nullable": True
                        }
                    },
                    "required": ["scenario", "timeframe", "contribution", "frequency"]
                },
                "descriptive_text": {
                    "type": "string",
                    "description": "Free-form explanation of what the user is asking"
                }
            },
            "required": ["intent", "entities", "descriptive_text"]
        }

     # Ask Gemini with schema enforcement
        response = model.generate_content(
            contents=(
                f"{user_context} "
                "You are a financial advisor specializing in Australian superannuation. "
                "Analyze the query, extract structured fields, and provide a free-text summary. "
                f"Query: {query}"
            ),
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json", response_schema=schema)
        )

        print("Raw Gemini Response:", response.text)

        try:
            result = json.loads(response.text)
        except json.JSONDecodeError:
            result = parse_fallback(query)
            # add descriptive_text to fallback as well
            result["descriptive_text"] = f"Fallback parse: User asked '{query}'"

        # Logging
        log_metadata({
            "service": "gemini_service",
            "user_id": user_id,
            "query": query,
            "intent": result.get("intent", "unknown"),
            "status": "success"
        })

        return result

    except ValueError as ve:
        log_metadata({"service": "gemini_service", "user_id": user_id,
                     "query": query, "error": str(ve), "status": "error"})
        raise
    except GoogleAPIError as gae:
        log_metadata({"service": "gemini_service", "user_id": user_id,
                     "query": query, "error": str(gae), "status": "error"})
        raise GoogleAPIError(f"Gemini API error: {str(gae)}")
    except Exception as e:
        log_metadata({"service": "gemini_service", "user_id": user_id,
                     "query": query, "error": str(e), "status": "error"})
        raise Exception(f"Unexpected error in Gemini service: {str(e)}")


if __name__ == "__main__":
    user_id = "user_123"
    test_queries = [
        "How will a recession affect my super in 20 years?",
        "If I contribute $20k quarterly, what happens in 10 years?",
        "Will my super drop if I put 15,000 bi-annual?",
        "What if I add $5k every 4 months for 30 years?",
        "How does a recession affect my super if I invest yearly?",
        "What’s the impact of a balanced fund on my super?",
        "Is low risk better for my super in a recession?"
    ]
    for q in test_queries:
        print("\nQuery:", q)
        response = process_query_with_gemini(q, user_id)
        print("Parsed Response:", json.dumps(response, indent=2))