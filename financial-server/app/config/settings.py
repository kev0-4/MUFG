from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pydantic import Field
import os

class Settings(BaseSettings):
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_ignore_empty=True,
        extra='allow',  # Allows undefined env vars like NLP_SERVICE_URL without errors
        case_sensitive=False
    )
    
    # API Configuration
    # alpha_vantage_api_key: str = "demo"  # Removed as Alpha Vantage is no longer used
    yahoo_finance_enabled: bool = True
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env='HOST')
    port: int = Field(default=8001, env='PORT')
    debug: bool = Field(default=False, env='DEBUG')
    log_level: str = Field(default="INFO", env='LOG_LEVEL')
    
    # Cache Configuration (Commented out if not used)
    # cache_type: str = "file"  # file or redis
    # cache_ttl_seconds: int = 3600
    # cache_dir: str = "./cache"
    # redis_url: Optional[str] = None
    
    # Rate Limiting
    yahoo_finance_rate_limit: int = Field(default=2000, env='YAHOO_FINANCE_RATE_LIMIT')
    
    # Development
    mock_data_enabled: bool = Field(default=False, env='MOCK_DATA_ENABLED')
    
    # Integration URLs
    nlp_service_url: str = Field(default='http://localhost:8000', env='NLP_SERVICE_URL')
    firebase_database_url: str = Field(default='https://finguard-b3ed2-default-rtdb.firebaseio.com', env='FIREBASE_DATABASE_URL')

# Global settings instance
settings = Settings()
