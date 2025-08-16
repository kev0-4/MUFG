import logging
import logging.config
import os
from datetime import datetime
from typing import Dict, Any
from app.config.settings import settings

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": settings.log_level,
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filename": "logs/financial_server.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8",
        },
    },
    "loggers": {
        "": {  # root logger
            "level": settings.log_level,
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

def setup_logging():
    """Initialize logging configuration"""
    logging.config.dictConfig(LOGGING_CONFIG)

def log_metadata(meta: Dict[str, Any]):  # FIXED: Added colon after 'meta'
    """Log structured metadata for tracking API calls and performance"""
    logger = logging.getLogger("financial_service")
    
    # Create structured log entry
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "service": meta.get("service", "financial_service"),  # Changed to 'meta' to match parameter name
        "function": meta.get("function", "unknown"),
        "user_id": meta.get("user_id", "anonymous"),
        "status": meta.get("status", "unknown"),
        "duration_ms": meta.get("duration_ms"),
        "cache_hit": meta.get("cache_hit", False),
        "api_source": meta.get("api_source"),
        "error": meta.get("error"),
    }
    
    # Log at appropriate level based on status
    if meta.get("error"):
        logger.error(f"API_CALL_ERROR: {log_entry}")
    elif meta.get("status") == "rate_limit_exceeded":
        logger.warning(f"RATE_LIMIT_EXCEEDED: {log_entry}")
    else:
        logger.info(f"API_CALL: {log_entry}")

# Initialize logging when module is imported
setup_logging()
