import os
from typing import Dict, Optional
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError
from config.settings import GEMINI_API_KEY
from services.user_data_service import fetch_user_data
from utils.logger import log_metadata
import json


def generate_eli5_response(simulation_data: Dict[str, any], user_id: str, news_context: Optional[Dict[str, any]] = None, ai_prompt: Optional[str] = None) -> Dict[str, any]:
    """
    Generate a dynamic simplified ELI5 explanation for financial simulation data using Gemini.

    Args:
        simulation_data (Dict[str, any]): Simulation results (e.g., {"projected_balance": 500000, "scenario": "recession", "timeframe": 20, "risk_level": "balanced"}).
        user_id (str): Unique user identifier for logging and context.
        news_context (Optional[Dict[str, any]]): News sentiment and summary (e.g., {"sentiment": -0.5, "summary": "Economic downturn predicted"}).
        ai_prompt (Optional[str]): Optional prompt from Gemini or other AI to incorporate (e.g., "Emphasize long-term saving").

    Returns:
        Dict[str, any]: Dictionary with simulation_data, news_context, and eli5_response.

    Raises:
        ValueError: If simulation_data is empty or invalid.
        GoogleAPIError: If Gemini API call fails.
        Exception: If response generation fails.
    """
    try:
        if not simulation_data or not isinstance(simulation_data, dict):
            raise ValueError("Simulation data must be a non-empty dictionary")

        # Fetch user data for personalization
        user_data = fetch_user_data(user_id)

        # Load system prompt from text file and replace variables
        system_prompt = load_and_compile_system_prompt(
            user_data=user_data,
            simulation_data=simulation_data,
            news_context=news_context,
            ai_prompt=ai_prompt
        )

        # Configure Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(
            "gemini-2.5-flash",
            system_instruction=system_prompt
        )

        # Create user message with the data to analyze
        user_message = f"""
Please analyze this data and provide an ELI5 explanation:

Simulation Data: {json.dumps(simulation_data)}
News Context: {json.dumps(news_context) if news_context else 'None'}
User Query: {ai_prompt if ai_prompt else "What does this mean for my retirement?"}
"""

        # Call Gemini for dynamic response
        response = model.generate_content(user_message)

        # Try to parse JSON response, fallback to plain text if needed
        try:
            # Check if response is JSON
            response_text = response.text.strip()
            if response_text.startswith('{') and response_text.endswith('}'):
                eli5_data = json.loads(response_text)
                eli5_response = eli5_data.get('eli5_response', eli5_data)
            else:
                # Plain text response - structure it
                eli5_response = {
                    "main_explanation": response_text,
                    "key_takeaway": "Review the explanation above for key insights about your retirement planning.",
                    "confidence_boost": "You're taking positive steps by learning about your financial future!"
                }
        except json.JSONDecodeError:
            # Fallback for non-JSON responses
            eli5_response = {
                "main_explanation": response.text.strip(),
                "key_takeaway": "Check your response for key insights about your retirement.",
                "confidence_boost": "You're on the right track with your retirement planning!"
            }

        # Ensure we return the expected format for backward compatibility
        if isinstance(eli5_response, str):
            eli5_text = eli5_response
        else:
            eli5_text = eli5_response.get(
                'main_explanation', str(eli5_response))

        # Prepare return dict - maintaining original format
        result = {
            "simulation_data": simulation_data,
            "news_context": news_context,
            "eli5_response": eli5_text  # Keep original string format for compatibility
        }

        log_metadata({
            "service": "eli5_service",
            "function": "generate_eli5_response",
            "user_id": user_id,
            "simulation_data": simulation_data,
            "news_context": news_context,
            "ai_prompt": ai_prompt,
            "eli5_response": eli5_text[:50] if isinstance(eli5_text, str) else str(eli5_text)[:50],
            "status": "success"
        })

        return result

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
    except GoogleAPIError as gae:
        log_metadata({
            "service": "eli5_service",
            "function": "generate_eli5_response",
            "user_id": user_id,
            "simulation_data": simulation_data,
            "error": str(gae),
            "status": "error"
        })
        raise GoogleAPIError(f"Gemini API error: {str(gae)}")
    except Exception as e:
        log_metadata({
            "service": "eli5_service",
            "function": "generate_eli5_response",
            "user_id": user_id,
            "simulation_data": simulation_data,
            "error": str(e),
            "status": "error"
        })
        raise Exception(
            f"Unexpected error in ELI5 response generation: {str(e)}")


def load_and_compile_system_prompt(user_data: Dict, simulation_data: Dict, news_context: Optional[Dict] = None, ai_prompt: Optional[str] = None) -> str:
    """Load the system prompt from file and replace template variables."""

    # Try multiple possible locations for the prompt file
    possible_paths = [
        os.path.join(os.path.dirname(__file__), 'prompts', 'eli5prompt.txt'),
        os.path.join(os.path.dirname(__file__), 'eli5prompt.txt'),
        os.path.join(os.getcwd(), 'prompts', 'eli5prompt.txt'),
        os.path.join(os.getcwd(), 'eli5prompt.txt'),
        'eli5prompt.txt'  # Current directory
    ]

    system_prompt = None
    for prompt_path in possible_paths:
        if os.path.exists(prompt_path):
            try:
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    system_prompt = f.read().strip()
                    break
            except Exception as e:
                print(f"Warning: Error reading prompt file {prompt_path}: {e}")
                continue

    # Fallback prompt if file not found
    if not system_prompt:
        print("Warning: eli5prompt.txt not found, using fallback prompt")
        system_prompt = get_fallback_prompt()

    # Prepare template variables
    template_vars = {
        "user_age": user_data.get('age', 'unknown'),
        "user_risk_tolerance": user_data.get('risk_tolerance', 'unknown'),
        "user_super_balance": user_data.get('super_balance', 'unknown'),
        "projected_balance": simulation_data.get('projected_balance', 0),
        "risk_level": simulation_data.get('risk_level', 'medium'),
        "scenario": simulation_data.get('scenario', 'None'),
        "timeframe": simulation_data.get('timeframe', 'unknown'),
        "contribution": simulation_data.get('contribution', 'unknown'),
        "frequency": simulation_data.get('frequency', 'unknown'),
        "news_sentiment": news_context.get('sentiment', 0.5) if news_context else 0.5,
        "news_summary": news_context.get('summary', 'No current market news') if news_context else 'No current market news',
        "additional_prompt": ai_prompt if ai_prompt else "",
        "simulation_data_json": json.dumps(simulation_data),
        "news_context_json": json.dumps(news_context) if news_context else "null"
    }

    # Replace template variables
    compiled_prompt = replace_template_variables(system_prompt, template_vars)

    return compiled_prompt


def replace_template_variables(template: str, variables: Dict[str, any]) -> str:
    """
    Replace template variables in the prompt text.
    Supports both {variable} and {{variable}} formats.
    """
    result = template

    for key, value in variables.items():
        # Replace both single and double brace formats
        result = result.replace(f"{{{key}}}", str(value))
        result = result.replace(f"{{{{{key}}}}}", str(value))

    return result


def get_fallback_prompt() -> str:
    """Fallback system prompt if eli5prompt.txt is not found."""
    return """
You are Riley, a friendly Australian retirement advisor who specializes in explaining complex financial concepts to everyday Aussies in the simplest possible terms.

You're like that helpful mate who actually understands superannuation and can explain it without the confusing jargon that makes people's eyes glaze over.

Your personality:
- Patient and encouraging, never condescending
- Uses Australian terminology and cultural references
- Loves analogies involving everyday Australian experiences (BBQs, footy, road trips, etc.)
- Celebrates small wins and progress
- Acknowledges that money talk can be overwhelming
- Always focuses on actionable, simple steps

Your task is to take complex retirement simulation data and market news, then explain it like you're talking to a 5-year-old (but one who pays taxes and has a super account).

User Context:
- Age: {user_age}
- Risk tolerance: {user_risk_tolerance}
- Current super balance: ${user_super_balance}

Current Analysis:
- Projected balance: ${projected_balance}
- Risk level: {risk_level}
- Scenario: {scenario}
- Timeframe: {timeframe} years
- Contribution: ${contribution}
- Frequency: {frequency}
- News sentiment: {news_sentiment} (0.0 = negative, 1.0 = positive)
- News summary: {news_summary}

Additional instructions: {additional_prompt}

Guidelines:
- Keep paragraphs short (2-3 sentences max)
- Use Australian terminology ("super" not "superannuation")
- Include relevant emojis to keep it friendly (🏠💰🎯📈)
- Replace financial jargon with plain English
- Use relatable Australian analogies
- Keep it positive and encouraging
- Generate a short, engaging explanation (100-150 words)
- Focus on what this means for their retirement in simple terms

Respond with a clear, friendly explanation that helps them understand their financial situation without overwhelming them.
"""


# if __name__ == "__main__":
#     user_id = "user_123"
#     test_cases = [
#         {
#             "simulation_data": {
#                 "projected_balance": 500000,
#                 "scenario": "recession",
#                 "timeframe": 20,
#                 "risk_level": "balanced"
#             },
#             "news_context": {
#                 "sentiment": -0.5,
#                 "summary": "Mock: 2% Economic Downturn Predicted for Australia in 2025"
#             },
#             "ai_prompt": "Emphasize long-term saving despite challenges."
#         },
#         {
#             "simulation_data": {
#                 "projected_balance": 750000,
#                 "timeframe": 10,
#                 "contribution": 20000,
#                 "frequency": "quarterly"
#             },
#             "news_context": None,
#             "ai_prompt": None
#         },
#         {
#             "simulation_data": {
#                 "projected_balance": 300000,
#                 "risk_level": "low",
#                 "scenario": None
#             },
#             "news_context": {
#                 "sentiment": 0.7,
#                 "summary": "Mock: Superannuation Market Stable in 2025"
#             },
#             "ai_prompt": "Use a tree-growing analogy."
#         }
#     ]

#     for case in test_cases:
#         print("\nSimulation Data:", case["simulation_data"])
#         print("News Context:", case["news_context"])
#         print("AI Prompt:", case["ai_prompt"])
#         result = generate_eli5_response(
#             case["simulation_data"], user_id, case["news_context"], case["ai_prompt"])
#         print("Result:", result)
