from typing import Dict, List, Optional, Union, Any
from transformers import pipeline
from config.settings import FINANCIAL_DATA_API
from utils.logger import log_metadata
from services.user_data_service import fetch_user_data
from services.news_service import get_news_for_queries
from statistics import mean

# Initialize Hugging Face pipeline for sentiment analysis (loaded once for performance)
sentiment_pipeline = pipeline(
    "sentiment-analysis", model="distilbert-base-uncased"
)


def analyze_sentiment(text: str, user_id: str) -> Dict[str, Any]:
    """
    Analyze sentiment of a query or news article using Hugging Face's sentiment analysis pipeline.
    Supports long texts by chunking into 512-token segments.

    Args:
        text (str): Text to analyze (query or news article).
        user_id (str): Unique user identifier for logging.

    Returns:
        Dict[str, Any]: Sentiment score and label (e.g., {"score": -0.5, "label": "NEGATIVE"}).
    """
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

    try:
        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")

        print(f"🔹 Analyzing text of length {len(text)} characters")
        tokens = tokenizer(text)["input_ids"]
        print(f"🔹 Tokenized length: {len(tokens)}")

        max_len = 350
        chunk_scores = []

        # Split tokens into chunks
        for i in range(0, len(tokens), max_len):
            chunk_tokens = tokens[i:i + max_len]
            chunk_text = tokenizer.decode(
                chunk_tokens, skip_special_tokens=True)
            print(
                f"🔹 Processing chunk {i//max_len + 1} with {len(chunk_tokens)} tokens")

            result = sentiment_pipeline(chunk_text)[0]
            score = result["score"] if result["label"] == "POSITIVE" else - \
                result["score"]
            chunk_scores.append(score)

        avg_score = round(sum(chunk_scores) / len(chunk_scores), 2)
        label = "POSITIVE" if avg_score > 0 else "NEGATIVE" if avg_score < 0 else "NEUTRAL"

        response = {"score": avg_score, "label": label}

        log_metadata({
            "service": "nlp_service",
            "function": "analyze_sentiment",
            "user_id": user_id,
            "text": text[:50],
            "sentiment": response,
            "status": "success"
        })

        return response

    except Exception as e:
        log_metadata({
            "service": "nlp_service",
            "function": "analyze_sentiment",
            "user_id": user_id,
            "text": text[:50] if text else "",
            "error": str(e),
            "status": "error"
        })
        raise Exception(f"Unexpected error in sentiment analysis: {str(e)}")


def fetch_news_sentiment(
    query: str,
    user_id: str,
    intent: str,
    entities: Dict[str, Any],
    holdings: Optional[Dict[str, Any]] = None  # 👈 Optional parameter
) -> Dict[str, Any]:
    """
    Fetch and analyze sentiment of news articles relevant to the query using get_news_for_queries.
    Optionally include holdings/stocks to refine searches.

    Args:
        query (str): User query to guide news fetching.
        user_id (str): Unique user identifier for logging.
        intent (str): Intent from gemini_service (e.g., "scenario_simulation").
        entities (Dict[str, Any]): Entities from gemini_service (e.g., {"scenario": "recession"}).
        holdings (Dict[str, Any], optional): User's current holdings/stocks (e.g., {"stocks": ["BHP", "Rio Tinto"]})

    Returns:
        Dict[str, Any]: News sentiment and summary (e.g., {"sentiment": -0.5, "summary": "Economic downturn predicted"}).

    Raises:
        ValueError: If query is empty or invalid.
        Exception: If news fetch or analysis fails.
    """
    try:
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")

        # Generate dynamic search terms
        search_terms = []
        if intent == "scenario_simulation" and entities.get("scenario"):
            search_terms.append(
                f"Australian superannuation {entities['scenario']}")
            search_terms.append(f"{entities['scenario']} super fund 2025")
        if entities.get("investment_type"):
            search_terms.append(
                f"{entities['investment_type']} super fund Australia")
        if entities.get("risk_tolerance"):
            search_terms.append(
                f"{entities['risk_tolerance']} risk superannuation Australia")

        # Fallback broad query
        search_terms.append("Australian superannuation market trends 2025")

        # Fetch user context to refine queries
        user_data = fetch_user_data(user_id)
        if user_data.get("risk_tolerance"):
            search_terms.append(
                f"{user_data['risk_tolerance']} super fund Australia")
        if user_data.get("age"):
            search_terms.append(
                f"superannuation retirement age {user_data['age']} Australia")

        # ✅ Include holdings if provided
        if holdings:
            if isinstance(holdings, dict):
                for key, values in holdings.items():
                    if isinstance(values, list):
                        for val in values:
                            search_terms.append(f"{val} stock Australia")
                            search_terms.append(f"{val} superannuation impact")
                            search_terms.append(f"{val} financial news 2025")
                    else:
                        search_terms.append(f"{values} stock Australia")

        # Deduplicate search terms
        search_terms = list(set(search_terms))

        # Fetch news articles
        articles = get_news_for_queries(search_terms)
        # print(articles)
        if not articles:
            mock_response = {
                "sentiment": 0.0,
                "summary": "Mock news: No relevant articles found, defaulting to neutral sentiment."
            }
            log_metadata({
                "service": "nlp_service",
                "function": "fetch_news_sentiment",
                "user_id": user_id,
                "query": query[:50],
                "search_terms": search_terms,
                "response": mock_response,
                "status": "success (mock)"
            })
            return mock_response

        # Analyze sentiment for each article
        sentiments = [analyze_sentiment(
            article["content"], user_id) for article in articles]

        # Aggregate sentiment (average score)
        avg_sentiment = round(mean([s["score"] for s in sentiments]), 2)

        # Select article with highest absolute sentiment for summary
        max_sentiment_article = max(sentiments, key=lambda x: abs(x["score"]))
        summary_article = next(a for a, s in zip(
            articles, sentiments) if s["score"] == max_sentiment_article["score"])

        response = {
            "sentiment": avg_sentiment,
            "summary": summary_article["title"]
        }

        log_metadata({
            "service": "nlp_service",
            "function": "fetch_news_sentiment",
            "user_id": user_id,
            "query": query[:50],
            "search_terms": search_terms,
            "response": response,
            "article_count": len(articles),
            "status": "success"
        })

        return response

    except ValueError as ve:
        log_metadata({
            "service": "nlp_service",
            "function": "fetch_news_sentiment",
            "user_id": user_id,
            "query": query[:50] if query else "",
            "error": str(ve),
            "status": "error"
        })
        raise
    except Exception as e:
        log_metadata({
            "service": "nlp_service",
            "function": "fetch_news_sentiment",
            "user_id": user_id,
            "query": query[:50] if query else "",
            "error": str(e),
            "status": "error"
        })
        raise Exception(
            f"Unexpected error in news sentiment analysis: {str(e)}")


# if __name__ == "__main__":
#     user_id = "user_123"
#     test_cases = [
#         {"query": "How will a recession affect my super in 20 years?",
#             "intent": "scenario_simulation", "entities": {"scenario": "recession", "timeframe": 20}},
#         {"query": "If I contribute $20k quarterly, what happens in 10 years?", "intent": "super_projection",
#             "entities": {"contribution": 20000, "frequency": "quarterly", "timeframe": 10}},
#         {"query": "Will my super drop if I put 15,000 bi-annual?", "intent": "super_projection",
#             "entities": {"contribution": 15000, "frequency": "bi-annual"}},
#         {"query": "What’s the impact of a balanced fund on my super?",
#             "intent": "general_query", "entities": {"investment_type": "balanced_fund"}},
#         {"query": "Is low risk better for my super in a recession?", "intent": "scenario_simulation",
#             "entities": {"risk_tolerance": "low", "scenario": "recession"}}
#     ]

#     for case in test_cases:
#         print(f"\nQuery: {case['query']}")
#         sentiment = analyze_sentiment(case["query"], user_id)
#         print("Sentiment:", sentiment)
#         news_sentiment = fetch_news_sentiment(
#             case["query"], user_id, case["intent"], case["entities"])
#         print("News Sentiment:", news_sentiment)
"""
Expected return response
News Sentiment: {'sentiment': -0.57, 'summary': 'AMP becomes first major super fund to offer cashback rewards that boost your super balance - AdviserVoice'}
"""