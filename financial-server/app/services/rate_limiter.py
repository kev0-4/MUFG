import json
import os
from datetime import datetime, timedelta
from typing import Dict
from app.config.settings import settings
from app.utils.logger import log_metadata

class RateLimiter:
    def __init__(self):
        self.rate_limit_file = "rate_limits.json"
        self.limits = {
            "yahoo_finance": settings.yahoo_finance_rate_limit
        }
    
    def _load_rate_data(self) -> Dict:
        """Load rate limiting data from file"""
        try:
            if os.path.exists(self.rate_limit_file):
                with open(self.rate_limit_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception:
            return {}
    
    def _save_rate_data(self, data: Dict):
        """Save rate limiting data to file"""
        try:
            with open(self.rate_limit_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            log_metadata({
                "function": "save_rate_data",
                "status": "error",
                "error": str(e)
            })
    
    def can_make_request(self, api_name: str) -> bool:
        """Check if API request is within rate limits"""
        try:
            rate_data = self._load_rate_data()
            now = datetime.utcnow()
            day_key = now.strftime("%Y-%m-%d")
            api_key = f"{api_name}_{day_key}"
            
            if api_key not in rate_data:
                rate_data[api_key] = {
                    "count": 0,
                    "reset_at": (now + timedelta(days=1)).isoformat()
                }
            
            # Check if reset time has passed
            reset_time = datetime.fromisoformat(rate_data[api_key]["reset_at"])
            if now >= reset_time:
                rate_data[api_key] = {
                    "count": 0,
                    "reset_at": (now + timedelta(days=1)).isoformat()
                }
            
            # Check rate limit
            current_count = rate_data[api_key]["count"]
            limit = self.limits.get(api_name, 1000)
            
            if current_count >= limit:
                log_metadata({
                    "function": "rate_limiter", 
                    "status": "rate_limit_exceeded",
                    "api_name": api_name,
                    "current_count": current_count,
                    "limit": limit
                })
                return False
            
            # Increment counter
            rate_data[api_key]["count"] += 1
            self._save_rate_data(rate_data)
            
            return True
            
        except Exception as e:
            log_metadata({
                "function": "rate_limiter",
                "status": "error",
                "api_name": api_name,
                "error": str(e)
            })
            return False

# Global rate limiter instance
rate_limiter = RateLimiter()
