# src/config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configurações da aplicação usando Pydantic Settings."""
    
    # Database
    DATABASE_URL: str
    DATABASE_URL_SYNC: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str
    REDIS_MAX_CONNECTIONS: int = 50
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    API_TITLE: str = "Sistema de Monitoramento Judicial"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str
    
    # Scraping
    MAX_CONCURRENT_REQUESTS: int = 10
    REQUEST_TIMEOUT: int = 30
    USER_AGENT: str = "Mozilla/5.0 (compatible; JudicialBot/1.0)"
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 5
    
    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    
    # Cache
    CACHE_TTL: int = 3600
    CACHE_ENABLED: bool = True
    
    # Monitoring
    ENABLE_METRICS: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()