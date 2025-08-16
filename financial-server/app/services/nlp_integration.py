import httpx
from typing import Dict, Any, Optional
from app.config.settings import settings
from app.utils.logger import log_metadata


class NLPIntegration:
    def __init__(self, nlp_service_url: str = settings.nlp_service_url):
        self.nlp_service_url = nlp_service_url
        self.timeout = 30.0
    
    async def query_nlp(self, query: str, user_id: str = "anonymous") -> Optional[Dict[str, Any]]:
        """Call NLP /query endpoint for intent, entities, and sentiment analysis"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.nlp_service_url}/nlp/query",
                    json={"query": query, "user_id": user_id}
                )
                response.raise_for_status()
                
                result = response.json()
                
                log_metadata({
                    "function": "nlp_query",
                    "user_id": user_id,
                    "status": "success",
                    "query_length": len(query)
                })
                
                return result
                
        except Exception as e:
            log_metadata({
                "function": "nlp_query", 
                "user_id": user_id,
                "status": "error",
                "error": str(e)
            })
            return None
    
    async def enhance_nlp(
        self,
        simulation_data: Dict[str, Any],
        user_id: str = "anonymous",
        ai_prompt: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Call NLP /enhance endpoint for ELI5 explanations and sentiment enhancement"""
        payload = {
            "simulation_data": simulation_data,
            "user_id": user_id,
            "ai_prompt": ai_prompt
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.nlp_service_url}/nlp/enhance",
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                
                log_metadata({
                    "function": "nlp_enhance",
                    "user_id": user_id,
                    "status": "success"
                })
                
                return result
                
        except Exception as e:
            log_metadata({
                "function": "nlp_enhance", 
                "user_id": user_id,
                "status": "error",
                "error": str(e)
            })
            return None


# Global NLP integration instance
nlp_integration = NLPIntegration()