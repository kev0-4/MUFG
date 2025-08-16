import httpx
from typing import Dict, Any, Optional
from app.config.settings import settings
from app.utils.logger import log_metadata

class NLPIntegration:
    def __init__(self, nlp_service_url: str = "http://teammate-ip:8000"):
        self.nlp_service_url = nlp_service_url
        self.timeout = 30.0
    
    async def get_sentiment_analysis(self, text: str, user_id: str = "anonymous") -> Optional[Dict[str, Any]]:
        """Send text to NLP service for sentiment analysis"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.nlp_service_url}/api/sentiment",
                    json={"text": text, "user_id": user_id}
                )
                response.raise_for_status()
                
                result = response.json()
                
                log_metadata({
                    "function": "nlp_sentiment",
                    "user_id": user_id,
                    "status": "success",
                    "text_length": len(text)
                })
                
                return result
                
        except Exception as e:
            log_metadata({
                "function": "nlp_sentiment", 
                "user_id": user_id,
                "status": "error",
                "error": str(e)
            })
            return None

# Global NLP integration instance
nlp_integration = NLPIntegration()
