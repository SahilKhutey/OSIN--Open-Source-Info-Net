import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "OSIN: Open Source Info Net"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://osin_user:osin_password@db:5432/osin_intelligence")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda:29092")
    
    # AI Keys (Optional for initial setup)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    class Config:
        env_file = ".env"

settings = Settings()
