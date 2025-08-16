from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # API Configuration
    alpha_vantage_api_key: str = "demo"
    yahoo_finance_enabled: bool = True
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8001
    debug: bool = False
    log_level: str = "INFO"
    
    # Cache Configuration
    cache_type: str = "file"  # file or redis
    cache_ttl_seconds: int = 3600
    cache_dir: str = "./cache"
    redis_url: Optional[str] = None
    
    # Rate Limiting
    alpha_vantage_rate_limit: int = 25
    yahoo_finance_rate_limit: int = 2000
    
    # Development
    mock_data_enabled: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
